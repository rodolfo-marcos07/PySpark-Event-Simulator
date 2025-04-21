import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, window, sum as _sum, avg as _avg, round as _round
from pyspark.sql.types import StructType, StringType, IntegerType

# Ensure the input_stream directory exists
os.makedirs("input_stream", exist_ok=True)

# Initialize Spark session
spark = SparkSession.builder \
    .appName("StreamingWithOutOfOrderHandling") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Define schema for CSV
schema = StructType() \
    .add("event_time", StringType()) \
    .add("value", IntegerType())

# Read streaming CSV files
streaming_df = spark.readStream \
    .option("sep", ",") \
    .option("header", True) \
    .schema(schema) \
    .csv("input_stream")  # Folder to watch

# Parse string to timestamp
parsed_stream = streaming_df.withColumn("event_time", to_timestamp("event_time", "yyyy-MM-dd HH:mm:ss"))

# -------------------------
# 1. parsed_stream
# -------------------------
#   • Assumes your raw stream is parsed into a DataFrame with at least:
#       – event_time (timestamp)
#       – value      (numeric measurement)
#   • Feel free to rename or add fields (e.g., category, user_id, sensor_reading)

# -------------------------
# 2. Watermark – Handling Late Data
# -------------------------
# .withWatermark("event_time", "30 seconds")
#   • Accept events up to 30s late
#   • Try "2 minutes" if your source buffers longer, or "10 seconds" for low latency
#   • Remove it entirely to allow *all* late data (watch for resource growth!)

# -------------------------
# 3. Windowing – Time Buckets
# -------------------------
# .groupBy(window("event_time", "60 seconds"))
#   • “60 seconds” creates non-overlapping 1-minute windows
#   • Change to "300 seconds" for 5-minute summaries
#   • For sliding windows, pass both size and slide:
#       window("event_time", "60 seconds", "30 seconds")
#   • Swap to session windows for dynamic grouping:
#       session_window("event_time", "5 minutes")

# -------------------------
# 4. Aggregations – Build Your Metrics
# -------------------------
# .agg(
#     _avg("value").alias("value"),    # average per window
#     _sum("value").alias("value"),  # total sum in window
#     _max("value").alias("value")     # highest observed
# )
#   • Add count(), min(), stddev(), etc.
#   • Alias fields whatever makes sense for your dashboard

aggregated = (
    parsed_stream
      # handle late arrivals
    .withWatermark("event_time", "30 seconds")
      # bucket into fixed windows
    .groupBy(
        window("event_time", "60 seconds")    # try 5-minute or sliding windows too!
    )
      # compute metrics of interest
    .agg(
        _round(_avg("value"), 2).alias("value")
        # , _sum("value").alias("value")
        # , _max("value").alias("value")
    )
)

# === Next Steps & Experiments ===
# • Tweak watermark duration and observe how many late records get dropped vs. included.
# • Adjust window size and slide interval to capture bursty events or smoother averages.
# • Add extra grouping columns (e.g., category, region) to break down metrics.
# • Switch to session_window() for session-based analytics.
# • Plug into a real sink (Kafka, console, files) to visualize streaming results!

def process_batch(batch_df, batch_id):
    # Only write if the batch has data
    if not batch_df.isEmpty():
        # Write to a single JSON file
        batch_df.coalesce(1).write.mode("append").json("./output")

processesquery = aggregated.writeStream \
    .outputMode("update") \
    .foreachBatch(process_batch) \
    .option("checkpointLocation", "./checkpoint") \
    .trigger(processingTime="1 second") \
    .start()

processesquery.awaitTermination()