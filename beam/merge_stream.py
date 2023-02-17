import pymongo
import apache_beam as beam
from apache_beam.io.kafka import WriteToKafka

# MongoDB connection parameters
mongo_uri = 'mongodb://localhost:27017'
mongo_db = ['db1', 'db2', 'db3']

# Kafka connection parameters
kafka_servers = 'localhost:9092'
kafka_topic = 'productcollection'

# MongoDB reader class


class ReadFromMongoDB(beam.DoFn):
    def process(self, db):
        client = pymongo.MongoClient(mongo_uri)
        db = client[db]
        collection = db['productcollections']
        for document in collection.find():
            yield document


# Apache Beam pipeline
with beam.Pipeline() as pipeline:
    # Read data from MongoDB collections
    data_from_mongo = (
        pipeline
        | 'Create pipeline' >> beam.Create([db for db in mongo_db])
        | 'Read from MongoDB' >> beam.ParDo(ReadFromMongoDB())
        | beam.Reshuffle()
        | 'Write to Kafka' >> WriteToKafka(
            producer_config={'bootstrap.servers': kafka_servers},
            topic=kafka_topic,
            key_serializer='org.apache.kafka.common.serialization.StringSerializer',
            value_serializer='org.apache.kafka.common.serialization.StringSerializer'
        )
    )

    # # Transform the data (if necessary)
    # transformed_data = data_from_mongo | 'Apply transformations' >> beam.Map(
    #     lambda document: {'key': document['_id'], 'value': document})

    # # Write the data to Kafka
    # transformed_data | 'Write to Kafka' >> WriteToKafka(
    #     producer_config={'bootstrap.servers': kafka_servers},
    #     topic=kafka_topic,
    #     key_serializer='org.apache.kafka.common.serialization.StringSerializer',
    #     value_serializer='org.apache.kafka.common.serialization.StringSerializer'
    # )
