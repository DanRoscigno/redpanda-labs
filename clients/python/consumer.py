import os
import logging
from dotenv import load_dotenv
from kafka import (KafkaConsumer, TopicPartition)

load_dotenv()
logging.basicConfig(level=logging.INFO)

redpanda_brokers = os.getenv("REDPANDA_BROKERS")
kafka_security_protocol = os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")
kafka_sasl_mechanism = os.getenv("KAFKA_SASL_MECHANISM", None)
redpanda_username = os.getenv("REDPANDA_USERNAME", None)
redpanda_password = os.getenv("REDPANDA_PASSWORD", None)
logging.info("Connecting to: %s", redpanda_brokers)

#
# Read from topic
#
consumer = KafkaConsumer(
    bootstrap_servers=redpanda_brokers,    
    security_protocol=kafka_security_protocol,
    sasl_mechanism=kafka_sasl_mechanism,
    sasl_plain_username=redpanda_username,
    sasl_plain_password=redpanda_password,
    group_id=None,
    auto_offset_reset="earliest",
    enable_auto_commit="false",
    auto_commit_interval_ms=0,
    # ssl_cafile="ca.crt",
    # ssl_certfile="client.crt",
    # ssl_keyfile="client.key"
)

topic_name = os.getenv("REDPANDA_TOPIC_NAME", "test-topic")
assignments = []
partitions = consumer.partitions_for_topic(topic_name)
for p in partitions:
    assignments.append(TopicPartition(topic_name, p))
consumer.assign(assignments)
consumer.seek_to_beginning()

try:
    batch = consumer.poll(timeout_ms=10000)
    for records in batch.values():
        for r in records:
            out = f"topic: {r.topic}, "
            out += f"partition: {r.partition}, "
            out += f"offset: {r.offset}, "
            out += f"value: {r.value.decode()}"
            logging.info(out)
except Exception as e:
    logging.error(e)
finally:
    consumer.close()
