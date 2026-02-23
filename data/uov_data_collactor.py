import re
import json
import csv
import urllib.parse
from datetime import datetime
from playwright.sync_api import sync_playwright


# ============================================================
# User Configuration (edit only this block)
# ============================================================
CONFIG = {
    # Route object used in URL
    "route_obj": {
        "route_id": 68835,
        "route_long_name": "Wilhelminapark - Utrecht CS - Lunetten",
        "route_short_name": "8",
        "agency_id": "UOV",
    },

    # Query parameters
    "direction_id": 0,
    "date_display": "Tu 24 Feb",
    "year": 2026,
    # Don't change this parameter
    "time_hhmm": "00:00",

    # Runtime options
    "headless": True,
    "verbose": True,
    "output_csv": "uov_timetable_8.csv",
}


# ============================================================
# Utility Functions
# ============================================================
def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def parse_date_display_to_ddmmyyyy(date_display: str, year: int) -> str:
    """Convert display date (e.g. 'Tu 24 Feb') to 'dd-mm-yyyy'."""
    parts = (date_display or "").strip().split()
    if len(parts) < 2:
        raise ValueError(f"Bad date display: {date_display}")
    day = int(parts[-2])
    mon_str = parts[-1]
    dt = datetime.strptime(f"{day} {mon_str} {year}", "%d %b %Y")
    return dt.strftime("%d-%m-%Y")


def normalize_time_input(t: str) -> str:
    """Normalize time to HH:MM format."""
    t = (t or "").strip()
    m = re.match(r"^(\d{1,2}):(\d{2})$", t)
    if not m:
        raise ValueError(f"Bad time format: {t}")
    hh, mm = int(m.group(1)), int(m.group(2))
    return f"{hh:02d}:{mm:02d}"


def build_url(route_obj: dict, date_ddmmyyyy: str, time_hhmm: str, direction_id: int = 0) -> str:
    """Construct timetable URL."""
    route_enc = urllib.parse.quote(json.dumps(route_obj, separators=(",", ":")))
    return (
        "https://www.u-ov.nl/en/timetable?"
        f"route={route_enc}&date={date_ddmmyyyy}&time={urllib.parse.quote(time_hhmm)}"
        f"&directionId={direction_id}"
    )


def parse_hhmm_to_minutes(t: str) -> int:
    """Convert HH:MM (optionally with *) to sortable minutes."""
    if not t:
        return 10**9
    t = (t or "").strip()
    is_next_day = "*" in t
    t = t.replace("*", "")
    m = re.match(r"^(\d{2}):(\d{2})$", t)
    if not m:
        return 10**9
    minutes = int(m.group(1)) * 60 + int(m.group(2))
    return minutes + (24 * 60 if is_next_day else 0)


def trip_signature_full(trip: dict) -> str:
    """Generate unique signature for deduplication."""
    seq = trip.get("stops", []) or []
    parts = []
    for x in seq:
        ts = (x.get("timestamp") or "").strip()
        if ts:
            parts.append(ts)
        else:
            parts.append((x.get("time") or "").replace("*", "").strip())
    return "|".join(parts)


# ============================================================
# DOM Extraction
# ============================================================
def extract_trips_grouped_by_column_all_blocks(page, drop_empty_cells: bool = True) -> list[dict]:
    """
    Extract all timetable blocks and transpose
    (rows = stops, columns = trips).
    """
    stop_items = page.locator("ul.timetable__stops-info-list > li.timetable__stop")
    stop_items.first.wait_for(state="visible", timeout=20000)
    stops = [_clean(x) for x in stop_items.all_inner_texts()]
    stops = [s for s in stops if s]
    n_stops = len(stops)
    if n_stops == 0:
        return []

    rows = page.locator("ul.timetable__trips-stop")
    rows.first.wait_for(state="visible", timeout=20000)
    total_rows = rows.count()
    if total_rows == 0:
        return []

    n_blocks = total_rows // n_stops
    if n_blocks <= 0:
        return []

    trips_all: list[dict] = []
    trip_index = 0

    for b in range(n_blocks):
        block_rows = [rows.nth(b * n_stops + i) for i in range(n_stops)]

        matrix_time: list[list[str]] = []
        matrix_ts: list[list[str]] = []
        max_cols = 0

        for i in range(n_stops):
            time_cells = block_rows[i].locator("li.timetable__trips-time")
            times = [_clean(t) for t in time_cells.all_inner_texts()]

            ts_vals = []
            for k in range(time_cells.count()):
                ts_vals.append(_clean(time_cells.nth(k).get_attribute("data-timestamp") or ""))

            max_cols = max(max_cols, len(times))
            matrix_time.append(times)
            matrix_ts.append(ts_vals)

        for i in range(n_stops):
            if len(matrix_time[i]) < max_cols:
                pad_len = max_cols - len(matrix_time[i])
                matrix_time[i] += [""] * pad_len
                matrix_ts[i] += [""] * pad_len

        for j in range(max_cols):
            seq = []
            for i in range(n_stops):
                t = matrix_time[i][j]
                ts = matrix_ts[i][j]
                if drop_empty_cells and not t:
                    continue
                if t:
                    seq.append({"stop": stops[i], "time": t, "timestamp": ts})
            if seq:
                trip_index += 1
                trips_all.append({"trip_index": trip_index, "stops": seq})

    return trips_all


# ============================================================
# CSV Export
# ============================================================
def export_trips_to_csv(trips: list[dict], filename: str) -> None:
    """Export trips to CSV in long format."""
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["trip_index", "stop_sequence", "stop_name", "time", "timestamp"])

        for trip in trips:
            trip_index = trip["trip_index"]
            for seq_idx, item in enumerate(trip.get("stops", []) or [], start=1):
                raw_stop = item.get("stop", "")
                clean_stop = re.sub(r"^Information about the bus stop:\s*", "", raw_stop, flags=re.I)
                if "," in clean_stop:
                    clean_stop = clean_stop.split(",")[-1].strip()

                writer.writerow([
                    trip_index,
                    seq_idx,
                    clean_stop,
                    item.get("time", ""),
                    item.get("timestamp", ""),
                ])


# ============================================================
# Main Scraper
# ============================================================
def scrape_one_day(config: dict) -> list[dict]:
    """Scrape one day timetable with a single request."""
    route_obj = config["route_obj"]
    direction_id = int(config["direction_id"])
    date_ddmmyyyy = parse_date_display_to_ddmmyyyy(config["date_display"], int(config["year"]))
    time_hhmm = normalize_time_input(config["time_hhmm"])
    url = build_url(route_obj, date_ddmmyyyy, time_hhmm, direction_id)

    if config.get("verbose", False):
        print(f"[goto] {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=bool(config.get("headless", True)))
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(20000)
        page.set_default_navigation_timeout(45000)

        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector("ul.timetable__trips-stop li.timetable__trips-time", timeout=20000)

        trips = extract_trips_grouped_by_column_all_blocks(page)

        context.close()
        browser.close()

    # Deduplicate
    uniq = []
    seen = set()
    for t in trips:
        sig = trip_signature_full(t)
        if sig and sig not in seen:
            seen.add(sig)
            uniq.append(t)

    # Sort and reindex
    uniq.sort(key=lambda t: parse_hhmm_to_minutes((t.get("stops") or [{}])[0].get("time", "")))
    for idx, t in enumerate(uniq, start=1):
        t["trip_index"] = idx

    if config.get("verbose", False):
        print(f"[ok] trips(raw)={len(trips)} | trips(uniq)={len(uniq)}")

    return uniq



if __name__ == "__main__":
    trips = scrape_one_day(CONFIG)
    export_trips_to_csv(trips, CONFIG["output_csv"])
    print(f"CSV exported: {CONFIG['output_csv']} | trips={len(trips)}")