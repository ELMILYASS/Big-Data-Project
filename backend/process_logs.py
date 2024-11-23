import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, length, lit, sum as _sum, date_format, split, col

# Create Spark session
spark = SparkSession.builder.appName("SalesAggregation").getOrCreate()

# Function to process the log files and generate the report
def process_logs(input_dir, output_base_dir):

    # Check if the directory exists
    if not os.path.exists(input_dir):
        print(f"Log directory does not exist: {input_dir}")
        return

    # Get all log files in the directory, excluding .crc files
    log_files = [
        os.path.join(input_dir, f) for f in os.listdir(input_dir)
        if f.endswith('.txt') and not f.endswith('.crc')
    ]

    # Check if any log files exist
    if not log_files:
        print(f"No log files found in directory: {input_dir}")
        return

    print(f"Found log files: {log_files}")  # Debugging: print the list of files found

    # Read all the log files
    df = spark.read.text(log_files)

    # Show a few rows of the raw data for debugging
    print("Showing a few rows of the raw log data:")
    df.show(5, truncate=False)

    # Parse the logs into structured data (format the timestamp)
    df_parsed = df.select(
        to_timestamp(df['value'].substr(1, 19), 'yyyy/MM/dd HH:mm:ss').alias('timestamp'),
        df['value'].substr(lit(20), length(df['value']) - lit(19)).alias('log_data')
    )

    # Show the parsed dataframe
    print("Showing a few rows of the parsed data:")
    df_parsed.show(5, truncate=False)

    # Split the log data into individual columns
    df_split = df_parsed.withColumn(
        "action", split(df_parsed['log_data'], r'\|')[1]
    ).withColumn(
        "agent", split(df_parsed['log_data'], r'\|')[2]
    ).withColumn(
        "product", split(df_parsed['log_data'], r'\|')[3]
    ).withColumn(
        "price", split(df_parsed['log_data'], r'\|')[4].cast('double')
    ).withColumn(
        "route", split(df_parsed['log_data'], r'\|')[5]
    )

    # Show the split dataframe
    print("Showing a few rows of the split data:")
    df_split.show(5, truncate=False)

    # Filter the data based on the action ('BUY')
    df_filtered = df_split.filter(df_split['action'] == 'BUY')

    # Show the filtered data
    print("Showing a few rows of the filtered data (action == 'BUY'):")
    df_filtered.show(5, truncate=False)

    # Extract the date from the timestamp and group by date, hour, and product
    df_filtered = df_filtered.withColumn('hour', date_format(df_filtered['timestamp'], 'yyyy/MM/dd HH'))

    # Add a 'category' column based on the first element of the 'route' column
    df_filtered = df_filtered.withColumn(
        "category", split(df_filtered['route'], ' ')[0]
    )
    
    # Show the data after extracting the hour
    print("Showing a few rows of the data with the hour column:")
    df_filtered.show(5, truncate=False)
    df_filtered.select("timestamp", "action", "product", "hour", "category").show(5, truncate=False)
    
    # Aggregate the data by hour and product
    df_aggregated = df_filtered.groupBy(
        'hour',
        'product',
        'category'
    ).agg(
        _sum(col('price')).alias('total_price')  # Sum of price * quantity for each product
    )

    # Show the aggregated data
    print("Showing a few rows of the aggregated data:")
    df_aggregated.show(5, truncate=False)

    # Format the output to match the required format
    df_output = df_aggregated.select(
        'hour', 'product', 'category', 'total_price'
    ).orderBy('hour')

    # Show the final output dataframe
    print("Showing the final output before writing to disk:")
    df_output.show(5, truncate=False)

    # Group by hour (output_path) and write all rows for each output_path in one go
    # Create a new DataFrame with the formatted output
    def write_output(path, data):
        # Write all rows for the given output_path at once
        with open(path, 'w') as f:
            for row in data:
                output_data = f"{row['hour']}|{row['product']}|{row['category']}|{row['total_price']}"
                f.write(output_data + "\n")
        print(f"Data has been written to {path}")

    # Group data by the 'hour' to ensure we write per file
    df_output_rdd = df_output.rdd.map(lambda row: (row['hour'], row)).groupByKey()

    # For each group (output_path), write the data at once
    for hour, rows in df_output_rdd.collect():
        output_path = os.path.join(output_base_dir, f"{hour.replace('/', '').replace(' ', '')}.txt")
        write_output(output_path, rows)

# Specify input and output base directories
input_dir = "/app/processed_logs"  # Base directory for log files
output_base_dir = "/app/output"  # Base directory for output files

# Process the logs and generate the report
process_logs(input_dir, output_base_dir)

# Stop the Spark session
spark.stop()
