# Kafka Streetview Streaming Simulation

### Components

_1. Producers (Cameras)_

Each camera source acts as a Kafka producer.

_2. Kafka Topic: StreetviewImages_

All frames are streamed into a single Kafka topic named StreetviewImages.

_3. Consumer (Python + Apache Spark)_

The consumer is implemented using Spark Structured Streaming. It subscribes to the VideoStreaming topic using Kafka’s default consumption strategy.

These queries represent three independent input queues, each corresponding to one camera source. These will later serve as input streams for the AI violence detection model.

## How To Run?

This is the instruction how to run this project on window. The command when running server is different for linux users.

### Prerequisites

Before running the project, make sure you have the following installed and configured:

- Java _(version: 8.0)_
- Apache Spark
- Apache Kafka

Environment Variables Configured:

- `JAVA_HOME`
- `SPARK_HOME`
- `HADOOP_HOME`

Ensure Scala version compatibility between Spark and Kafka.

> [!CAUTION]
> You may need to set the Scala version in your SparkSession to 2.12 if you’re using Kafka 2.12.

> [!NOTE] > [This is the Kafka version that I used](https://downloads.apache.org/kafka/3.9.0/kafka_2.13-3.9.0.tgz)
>
> After downloading, extract the downloaded file to a convenient directory (e.g., C:/):

### Starting Server

```powershell
# change to the kafka directory
cd C:\kafka_2.13-3.9.0

# running zookeeper
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```

In a new terminal, running the kafka server by running:

```powershell
# change to the kafka directory
cd C:\kafka_2.13-3.9.0

# running kafka-server
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

### Running Producer

The producer simulates a camera by sending video frames (as byte arrays) into Kafka partitions.
To run 3 instances of camera:

```powershell
python Kafka_Producer.py
```

### Running Consumer

Running the StreamingQueries scripts to see the effects.
