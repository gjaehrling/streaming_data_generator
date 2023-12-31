{
    "tableName": "user_data",
    "tableType": "REALTIME",
    "segmentsConfig": {
      "timeColumnName": "sourceTime",
      "timeType": "MILLISECONDS",
      "schemaName": "user",
      "replication": "1",
      "replicasPerPartition": "1"
    },
    "tenants": {},
    "tableIndexConfig": {
      "loadMode": "MMAP",
      "streamConfigs": {
        "streamType": "kafka",
        "stream.kafka.consumer.type": "lowlevel",
        "stream.kafka.topic.name": "sales.user_data",
        "stream.kafka.decoder.class.name": "org.apache.pinot.plugin.stream.kafka.KafkaJSONMessageDecoder",
        "stream.kafka.consumer.factory.class.name": "org.apache.pinot.plugin.stream.kafka20.KafkaConsumerFactory",
        "stream.kafka.broker.list": "172.18.0.3:29092",
        "realtime.segment.flush.threshold.time": "3600000",
        "realtime.segment.flush.threshold.size": "50000",
        "stream.kafka.consumer.prop.auto.offset.reset": "smallest"
      }
    },
    "metadata": {
      "customConfigs": {}
    }
  }