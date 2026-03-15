# Import Libraries
import pandas as pd
import numpy as np

# Column Transformation Functions 
  
def transform_time(t):
        t = str(t)

        if "*" in t:
            t = t.replace("*", "")
            hour = int(t[:2]) + 24
            return f"{hour:02d}{t[2:]}"
        else:
            return t

def trip_duration(StartTime,EndTime):
  return int(EndTime[0:2]) * 60 + int(EndTime[3:]) - int(StartTime[0:2]) * 60 - int(StartTime[3:]) 

#Test
#transform_time("01:24*")
#trip_duration("22:13","23:12")

def timetable_2_pow(df):

    # Ensure numeric ordering fields are numeric
    df["trip_index"] = pd.to_numeric(df["trip_index"], errors="coerce")
    df["stop_sequence"] = pd.to_numeric(df["stop_sequence"], errors="coerce")

    # Clean time column (remove any *)
    df["time"] = df["time"].apply(transform_time)

    # Sort rows
    df = df.sort_values(["trip_index", "stop_sequence"]).reset_index(drop=True)

    # Extract start rows
    start_rows = df.loc[df.groupby("trip_index")["stop_sequence"].idxmin()].copy()
    start_rows = start_rows.sort_values("trip_index").reset_index(drop=True)

    # Extract end rows
    end_rows = df.loc[df.groupby("trip_index")["stop_sequence"].idxmax()].copy()
    end_rows = end_rows.sort_values("trip_index").reset_index(drop=True)

    # Build matrix
    pieces = pd.DataFrame({
        "piece_id": start_rows["trip_index"].astype(int).values,
        "start_station": start_rows["stop_name"].values,
        "end_station": end_rows["stop_name"].values,
        "start_time": start_rows["time"].values,
        "end_time": end_rows["time"].values
    })

    pieces["duration_min"] = pieces.apply(
        lambda row: trip_duration(row["start_time"], row["end_time"]),
        axis=1
    )

    # Final columns
    pieces = pieces[
        ["piece_id", "start_station", "end_station", "start_time", "end_time", "duration_min"]
    ]
    return pieces

## Code Execution ##
data=pd.read_csv('/data//uov_timetable_1.csv')
data2=pd.read_csv('/content/drive/MyDrive/UU/Period3/SMCS/Assignment/uov_timetable_1_rev.csv')

df1=timetable_2_pow(data)
df2=timetable_2_pow(data2)

# Concatenate both dataframes
merged = pd.concat([df1, df2], ignore_index=True)

# Create unique IDs
merged["id"] = range(1, len(merged) + 1)

# Get all unique station names from both columns
stations = pd.concat([merged["start_station"], merged["end_station"]]).unique()

# Create encoding dictionary
station_to_id = {station: i for i, station in enumerate(stations)}

# Apply encoding
merged["start_station_id"] = merged["start_station"].map(station_to_id)
merged["end_station_id"] = merged["end_station"].map(station_to_id)
final = merged[['id','start_station_id','end_station_id','start_time','end_time','duration_min']].reset_index(drop=True)

print(final.head(10))
