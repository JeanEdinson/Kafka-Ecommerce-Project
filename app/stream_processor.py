import json
from kafka import KafkaConsumer, KafkaProducer

bootstrap_server = "host.docker.internal:29092"
input_topic = "raw_events_ecom"
output_topic = "clean_events_ecom"
group_id = "silver-stream-processor"

VALID_EVENT_TYPES = ["PAGE_VIEW", "ADD_TO_CART", "PURCHASE"]

consumer = KafkaConsumer(
    input_topic,
    bootstrap_servers = bootstrap_server,
    group_id = group_id,
    auto_offset_reset = "earliest",
    enable_auto_commit = False,
    key_deserializer = lambda k: k.decode("utf-8") if k else None,
    value_deserializer = lambda v: json.loads(v.decode("utf-8"))
)

producer = KafkaProducer(
    bootstrap_servers=bootstrap_server,
    key_serializer=lambda k: k.encode("utf-8") if k else None,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def is_valid_event(event):

    if not event.get("customer_id"):
        return False
    if event.get("event_type") not in VALID_EVENT_TYPES:
        return False
    if event.get("amount") == None or event.get("amount") <=0:
        return False
    if not event.get("currency"):
        return False
    if event.get("is_valid") == False:
        return False
    return True

print("Starting Silver Stream Processor...")

for message in consumer:
    key = message.key
    event = message.value

    if is_valid_event(event):
        producer.send(
            topic=output_topic,
            key=key,
            value=event
        )
        print(f"Forwarded | key={key} | event_type={event.get("event_type")}")
    else:
        print(f"Dropped | key={key} | reason=invalid")

    consumer.commit()