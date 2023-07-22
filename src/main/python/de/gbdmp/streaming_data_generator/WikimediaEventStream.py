#!/usr/bin/python3

"""
Fetch user events from Wikimedia

Maintainer Gerd Jährling mail@gerd-jaehrling.de
"""

import sys
import json
from sseclient import SSEClient as EventSource
import argparse
from pathlib import Path
from confluent_kafka import Producer, KafkaException
import socket
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField, SerializationError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from uuid import uuid4

# import and configuration for logging
import logging
from logging import config

# configure logging:
project_root = str(Path(__file__).parents[6])
logging_config = project_root + "/src/main/python/resources/logging.ini"
config.fileConfig(logging_config)


def send_messages(message, topic, bootstrap_server_address, bootstrap_server_port):
    """
    method to send the message to the Kafka producer:

    :param message:
    :param bootstrap_server_address:
    :param bootstrap_server_port:
    :return: none
    """

    string_serializer = StringSerializer('utf_8')

    try:
        conf = {'bootstrap.servers': bootstrap_server_address + ":" + bootstrap_server_port,
                'client.id': socket.gethostname()}
        producer = Producer(conf)

        producer.produce(topic=topic,
                        key=string_serializer(str(uuid4())),
                        value=message.encode('utf-8'),
                        on_delivery=delivery_report)
    except KafkaException as e:
        logging.error("failed to produce message: {}".format(e))
        pass

    producer.flush()


def delivery_report(err, msg):
    """
    Reports the success or failure of a message delivery.
    Args:
        err (KafkaError): The error that occurred on None on success.
        msg (Message): The message that was produced or failed.
    """

    if err is not None:
        logging.error("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    logging.info('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))


def run(num_messages, topic, bootstrap_server_address, bootstrap_server_port):

    url = 'https://stream.wikimedia.org/v2/stream/recentchange'
    messages_count = 0

    # use the python ServerSideEventClient (SSEClient) to get the events:
    for event in EventSource(url):
        if event.event == 'message':
            try:
                event_data = json.loads(event.data)
                event_data_json = json.dumps(event_data)
            except ValueError:
                pass
            else:
                # filter out events, keep only article edits (mediawiki.recentchange stream)
                if event_data['type'] == 'edit':
                    messages_count += 1
                    logging.info(event_data_json)
                    try:
                        send_messages(event_data_json, topic, bootstrap_server_address, bootstrap_server_port)
                    except Exception as e:
                        print("failed")

        if 0 < int(num_messages) <= messages_count:
            print('Producer will be killed as {} events were producted'.format(num_messages))
            exit(0)


if __name__ == '__main__':
    """
        main method calling the run method with parameters from argparse:
    """

    parser = argparse.ArgumentParser("define the topic")
    parser.add_argument("--messages", help="set the number of messages to be produced. Set to -1 for infinite", required=True)
    parser.add_argument("--topic", help="define the name of the topic", required=True)
    parser.add_argument("--bootstrapserver", help="hostname or address of the kafka broker", required=True)
    parser.add_argument("--bootstrapserverport", help="port the kafka broker", required=True)
    parser.add_argument("--schemaregistry", help="hostname or address of the schema registry", required=True)
    parser.add_argument("--schemaregistryport", help="port for schema registry", required=True)
    args = parser.parse_args()

    try:
        logging.info("call run method with parameters: {}".format(args))
        run(args.messages, args.topic, args.bootstrapserver, args.bootstrapserverport)
    except Exception as e:
        logging.error("cannot call run method".format(e))
        sys.exit(1)
