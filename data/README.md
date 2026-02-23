- [link to download data](https://data.ndovloket.nl)
    - `netex`： Newest timetable for buses, trams in whole Netherlands. Consist different company's data.
    - `haltes`： All percise location of bus stopping spot.
    - `bezetting`： Crowding level inside the vehicle (occupancy rate).
    
- Additional historical data may be available on their research page: https://ndovloket.nl/research.html.

- Ways to analyze NeTEx (Network Timetable Exchange) file
    - Using python to convert to Pandas DataFrame.
    - Convert to GTFS format to show on map.

# Instructions of how to use the uov collector - Hu
`CONFIG = {
    # Route object used in URL
    "route_obj": {
        "route_id": 68835,
        "route_long_name": "Wilhelminapark - Utrecht CS - Lunetten",
        "route_short_name": "8",
        "agency_id": "UOV",
    },
    "direction_id": 0,
    "date_display": "Tu 24 Feb",
    "year": 2026,
    "time_hhmm": "00:00",
    "headless": True,
    "verbose": True,
    "output_csv": "uov_timetable_8.csv",
}`
Choose the number of bus you want on the uov website, and find parameters in URL.
For route_long_name, replace the "+" with space and there is no need to change the time_hhmm.