from python_cimis import CimisClient
from datetime import datetime, date, timedelta
import pandas as pd


# Initialize client with your API key
client = CimisClient(app_key='0f4bf3b67b1143db8a990d4419f54add')

date_format = "%Y-%m-%d"
# Get daily weather data for the last week
# end_date = date.today() - timedelta(days=1)
# start_date = end_date - timedelta(days=240)
start_date = datetime.strptime("2025-08-01", date_format)
end_date = datetime.strptime("2026-09-25", date_format)


weather_data = client.get_daily_data(
    targets=[105],  # Tranquility
    #targets= ["lat=36.82,lng=-120.17"],
    start_date=start_date,
    end_date=end_date,
    prioritize_scs=False,
    data_items=["day-precip"]
)

# Export to CSV
#csv_file = client.export_to_csv(weather_data)

# Convert to DataFrame
rows = []
for record in weather_data.get_all_records():
    row = {
        #'date': pd.to_datetime(record.date),
        'date': record.date,
        #'station': record.station,
        #'julian': record.julian
    }

    # Add all data values
    for key, value in record.data_values.items():
        row[f"{key}_value"] = float(value.value) if value.value else None
        #row[f"{key}_qc"] = value.qc
        #row[f"{key}_unit"] = value.unit

    rows.append(row)

df = pd.DataFrame(rows)
df.set_index('date', inplace=True)
df.to_excel('CIMIS_Station105_Precp_20250801_20260925.xlsx')
