import json
from kafka import KafkaConsumer
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd

bootstrap_server = "host.docker.internal:29092"
topic_name = "clean_events_ecom"
group_id = "snowflake-loader"

snowflake_config = {
    "user": "your_user",
    "password": "your_password",
    "account": "zg65971.sa-east-1.aws",
    "warehouse": "COMPUTE_WH",
    "database": "KAFKA_ECOMMERCE",
    "schema": "STREAMING_ECOMMERCE"
}

batch_size = 10

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers = bootstrap_server,
    group_id = group_id,
    enable_auto_commit = False,
    auto_offset_reset = "earliest",
    key_deserializer = lambda k: k.decode("utf-8") if k else None,
    value_deserializer = lambda v: json.loads(v.decode("utf-8"))
)

sf_conn = snowflake.connector.connect(**snowflake_config)

print("Connected to Snowflake")
print("Starting Kafka -> Snowflake Loader...")

buffer = []

def flush_to_snowflake(records):
    df_records = pd.DataFrame(records)
    df_records.columns = [c.upper() for c in df_records.columns]

    success, nchunksn, nrows, _ = write_pandas(
        conn = sf_conn,
        df = df_records,
        table_name = "KAFKA_EVENTS_ECOM_SILVER"
    )

    if not success:
        raise Exception("Snowflake insert failed")

    print(f"Inserted {nrows} rows into Snowflake")

for message in consumer:
    event = message.value
    buffer.append({
        "event_id": event["event_id"],
        "customer_id": event["customer_id"],
        "event_type": event["event_type"],
        "amount": event["amount"],
        "currency": event["currency"],
        "event_timestamp": event["event_timestamp"]
    })

    if len(buffer) >= batch_size:
        try:
            flush_to_snowflake(buffer)
            consumer.commit()
            buffer.clear()
        except Exception as e:
            print(f"Error inserting batch: {e}")

