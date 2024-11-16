import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, sum as _sum, date_format, split, col

# Create Spark session
spark = SparkSession.builder.appName("SalesAggregation").getOrCreate()

# Function to process the log files and generate the report
def process_logs(input_dir, output_base_dir):
    # Define the static directory to read from
    log_dir_path = os.path.join(input_dir, '2024110911')

    # Check if the directory exists
    if not os.path.exists(log_dir_path):
        print(f"Log directory does not exist: {log_dir_path}")
        return

    # Get all log files in the directory, excluding .crc files
    log_files = [
        os.path.join(log_dir_path, f) for f in os.listdir(log_dir_path)
        if f.endswith('.txt') and not f.endswith('.crc')
    ]

    # Check if any log files exist
    if not log_files:
        print(f"No log files found in directory: {log_dir_path}")
        return

    print(f"Found log files: {log_files}")  # Debugging: print the list of files found

    # Read all the log files
    df = spark.read.text(log_files)

    # Show a few rows of the raw data for debugging
    print("Showing a few rows of the raw log data:")
    df.show(5, truncate=False)

    # Parse the logs into structured data (format the timestamp)
    df_parsed = df.select(
        # Parse the timestamp from the log
        to_timestamp(df['value'].substr(1, 19), 'yyyy/MM/dd HH:mm:ss').alias('timestamp'),
        df['value'].substr(21, 100).alias('log_data')
    )

    # Show the parsed dataframe
    print("Showing a few rows of the parsed data:")
    df_parsed.show(5, truncate=False)

    # Split the log data into individual columns
    df_split = df_parsed.withColumn(
        "action", split(df_parsed['log_data'], r'\|')[0]  # Action (buy, etc.)
    ).withColumn(
        "product", split(df_parsed['log_data'], r'\|')[1]  # Product name
    ).withColumn(
        "quantity", split(df_parsed['log_data'], r'\|')[2].cast('int')  # Quantity (integer)
    ).withColumn(
        "price", split(df_parsed['log_data'], r'\|')[3].cast('double')  # Price (double)
    ).withColumn(
        "route", split(df_parsed['log_data'], r'\|')[4]  # Route (product detail, etc.)
    )

    # Show the split dataframe
    print("Showing a few rows of the split data:")
    df_split.show(5, truncate=False)

    # Filter the data based on the action ('buy')
    df_filtered = df_split.filter(df_split['action'] == 'buy')

    # Show the filtered data
    print("Showing a few rows of the filtered data (action == 'buy'):")
    df_filtered.show(5, truncate=False)

    # Extract the date from the timestamp and group by date, hour, and product
    df_filtered = df_filtered.withColumn('hour', date_format(df_filtered['timestamp'], 'yyyy/MM/dd HH'))

    # Show the data after extracting the hour
    print("Showing a few rows of the data with the hour column:")
    df_filtered.show(5, truncate=False)

    # Aggregate the data by hour and product
    df_aggregated = df_filtered.groupBy(
        'hour',
        'product'
    ).agg(
        _sum(col('price') * col('quantity')).alias('total_price')  # Sum of price * quantity for each product
    )

    # Show the aggregated data
    print("Showing a few rows of the aggregated data:")
    df_aggregated.show(5, truncate=False)

    # Format the output to match the required format
    df_output = df_aggregated.select(
        'hour', 'product', 'total_price'
    ).orderBy('hour')

    # Show the final output dataframe
    print("Showing the final output before writing to disk:")
    df_output.show(5, truncate=False)

    # Prepare the output data as a single string to write to the .txt file
    output_data = df_output.rdd.map(lambda row: f"{row['hour']}, {row['product']}, {row['total_price']}").collect()

    # Define the output file path
    output_path = os.path.join(output_base_dir, '202411091111.txt')

    # Write the result to a text file
    with open(output_path, 'w') as f:
        for line in output_data:
            f.write(line + "\n")
    
    print(f"Data has been written to {output_path}")

# Specify input and output base directories
input_dir = "/app/logs"  # Base directory for log files
output_base_dir = "/app/output"  # Base directory for output files

# Process the logs and generate the report
process_logs(input_dir, output_base_dir)

# Stop the Spark session
spark.stop()
