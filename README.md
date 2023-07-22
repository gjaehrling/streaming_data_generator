# README #

This README documents the usage of the python Streaming Data Generator.

Example of the parameters for running the data generator are: 
```
--topic sales.user_profiles --bootstrapserver broker --bootstrapserverport 9092 --schemaregistry schema-registry --schemaregistryport 8081
```

The parameters needs to be differentiated whether the data generator runs in local mode (from the host)
Running in local mode on the host, the following parameters apply: 

```
--topic sales.user_profiles
--bootstrapserver localhost
--bootstrapserverport 9092
--schemaregistry schema-registry
--schemaregistryport 8081
```

The successful connection to the schema-registry is depending on the definition of the KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://broker:29092,PLAINTEXT_HOST://localhost:9092 and the 
SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081
Running as docker container using docker-compose, the command is defined in the following way:

```
CMD [ "python", "./src/main/python/de/gbdmp/streaming_data_generator/Generator.py", \
        "--topic", "sales.user_data", \
        "--bootstrapserver", "broker", "--bootstrapserverport", "29092", \
        "--schemaregistry", "schema-registry", "--schemaregistryport", "8081"]
```

### What is this repository for? ###

* Summary of the parameters for running the Data Generator eiter in local mode, or as docker container using docker-compose
* running the python Streaming Data Generator
* Version 1.0.0
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up? ###

* Summary of set up
* Configuration
* Dependencies: zookeeper, broker, schema-registry
* Database configuration: none
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact