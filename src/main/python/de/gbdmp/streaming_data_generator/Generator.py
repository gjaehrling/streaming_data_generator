#!/usr/bin/python3

"""
Python Streaming Data Generator:
Generate random user data

Maintainer Gerd Jährling mail@gerd-jaehrling.de
"""

# -*- coding: utf-8 -*-

# imports:
import random
import sys
import time
import json
from faker import Faker
from confluent_kafka import Producer, KafkaException
import socket
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField, SerializationError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import argparse
import setdefaultencoding

# import and configuration for logging
import logging
from logging import config

# configure logging:
project_root = str(Path(__file__).parents[6])
logging_config = project_root + "/src/main/python/resources/logging.ini"
config.fileConfig(logging_config)


def produce_message():
    """
    produce messages for user-data using the Faker class

    :return: data a dictionary of the fake user attributes
    """
    faker = Faker(["en_US"])

    data = json.loads("{}")
    #data["id"] = random.getrandbits(8)
    data["id"] = random.getrandbits(32)
    data["name"] = faker.name()
    data["sex"] = random.choice("MF")
    data["address"] = str((faker.address()).replace("\n", " ").replace("\r", "").strip())
    data["city"] = str(faker.city())
    data["zip"] = str(faker.postcode())
    data["country"] = str(faker.current_country())
    data["phone"] = faker.phone_number()
    data["email"] = faker.safe_email()
    data["image"] = faker.image_url()
    data["date_of_birth"] = str(faker.date_of_birth())
    data["profession"] = faker.job()
    data["created_at"] = str(datetime.now())
    #data["updated_at"] = None
    data["sourceTime"] = round(time.time() * 1000)

    return data


class User(object):
    """
    User record object
    """

    def __init__(self, id, name, sex, address, city, zip, country, phone, email, image, date_of_birth, profession, created_at, updated_at, sourceTime):
        self.id = id
        self.name = name
        self.sex = sex
        self.address = address
        self.city = city
        self.zip = zip
        self.country = country
        self.phone = phone
        self.email = email
        self.image = image
        self.date_of_birth = date_of_birth
        self.profession = profession
        self.created_at = created_at
        self.updated_at = updated_at
        self.sourceTime = sourceTime


def user_to_dict(user, ctx):
    """
    Returns a dict representation of a User instance for serialization.
    Args:
        user (User): User instance.
        ctx (SerializationContext): Metadata pertaining to the serialization
            operation.
    Returns:
        dict: Dict populated with user attributes to be serialized.
    """

    # User._address must not be serialized; omit from dict
    return user


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


def run(topic, bootstrap_server, bootstrap_server_port, schema_registry, schema_registry_port):
    """
    main method containing the JSON schema, connection to the schema-registry and the loop producing
    messages

    :return: none
    """

    global json_serializer, string_serializer
    try:
        logging.info("read the schema file:")
        schema_file_path = project_root + "/src/main/python/resources/schema.json"

        # Read the contents of the schema file
        with open(schema_file_path, "r") as file:
            schema_contents = file.read()
    except FileNotFoundError:
        logging.error("could not find or read file with the JSON schema!")

    try:
        logging.info("get the hostname of the schema-registry")
        schema_registry_address = socket.gethostbyname(schema_registry)
    except:
        logging.info("cannot derive the schema-registry address, assuming ip 0.0.0.0")
        schema_registry_address = "0.0.0.0"

    try:
        logging.debug("connect to the schema registry".format(schema_registry))
        schema_registry_url = "http://" + schema_registry_address + ":" + schema_registry_port

        schema_registry_conf = {"url": schema_registry_url}
        schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    except Exception as e:
        logging.error("cannot connect to the schema registry {}".format(e))
        sys.exit(1)

    try:
        logging.debug("using string serializer and JSON serializer to serialise the message")
        string_serializer = StringSerializer('utf_8')
        json_serializer = JSONSerializer(str(schema_contents), schema_registry_client, user_to_dict)
    except SerializationError as se:
        logging.error("serialization not successful {}".format(se))

    try:
        logging.info("connect to the kafka broker using bootstrap-server: ".format(bootstrap_server))
        logging.info("get the bootstrap server ip from the hostname (for running as container)")
        bootstrap_server_address = socket.gethostbyname(bootstrap_server)
        # conf = {'bootstrap.servers': "localhost:9092", 'client.id': socket.gethostname()}   # working config when running on the host
        conf = {'bootstrap.servers': bootstrap_server_address + ":" + bootstrap_server_port, 'client.id': socket.gethostname()}
        producer = Producer(conf)
    except KafkaException as e:
        logging.error("cannot instantiate kafka producer: ".format(e))

    logging.info("Producing user records to topic {}. ^C to exit.".format(topic))
    while True:
        # Serve on_delivery callbacks from previous calls to produce()
        producer.poll(0.0)
        # get a new fake user-profile:

        try:
            user_profile = produce_message()
            user_profile_json = json.dumps(user_profile)
            producer.produce(topic=topic,
                             key=string_serializer(str(uuid4())),
                             #value=json_serializer(user_profile, SerializationContext(topic, MessageField.VALUE)),
                             value=user_profile_json.encode('utf-8'),
                             on_delivery=delivery_report)
            # logging.info(user_profile)

        except KeyboardInterrupt:
            break

    logging.info("\nFlushing records...")
    producer.flush()


if __name__ == '__main__':
    """
    main method using a parameter to the topic:
    """

    parser = argparse.ArgumentParser("define the topic")
    parser.add_argument("--topic", help="define the name of the topic", required=True)
    parser.add_argument("--bootstrapserver", help="hostname or address of the kafka broker", required=True)
    parser.add_argument("--bootstrapserverport", help="port the kafka broker", required=True)
    parser.add_argument("--schemaregistry", help="hostname or address of the schema registry", required=True)
    parser.add_argument("--schemaregistryport", help="port for schema registry", required=True)
    args = parser.parse_args()

    try:
        logging.info("call run method with parameters: ".format(args))
        run(args.topic, args.bootstrapserver, args.bootstrapserverport, args.schemaregistry, args.schemaregistryport)
    except Exception as e:
        logging.error("cannot call run method".format(e))
        sys.exit(1)