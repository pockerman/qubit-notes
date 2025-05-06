# qubit-note: Pub/Sub Model in Redis


## Overview

The <a href="https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern">publisher/subscriber model</a>
 is a well known pattern in software engineering. This is a messaging/communication pattern where publishers categorize messages into topics that are received by subscribers.

In this note I discuss how to implement the pattern using <a href="https://redis.io/">Redis</a>.

**keywords:** Redis, Python, pub-sub-pattern, system-design, software-architecture


## Pub/Sub model in Redis

When working with distributed applications, oftne we need to send some information
to other parts of the system as events happen. Doing this synchronously i.e. wait for the service to
recieve the message can seriously hurt the performance of our application.

One way to avoid this, is to use the Pub/Sub pattern. 
In this pattern, the sender puts the message into a message queue and the subscriber receives this message.
This may done via a broker that its job is to notify the subscriber that a message has arrived. This is shown schematically in the 
figure below. However, a subscriber may directly attempt to read a message from the queue when it's ready. In this case,
there is no broker involved but just some sort of storage that the receiver can read the messages from.

| ![publish-subscribe](./images/publish-subscribe.png)  |
|:-----------------------------------------------------------:|
|             **Figure 1: Pub/Sub schematics. Image from [3].**   |



We can use Redis as our message queue. Let's see how to do this. The _PUBLISH/SUBSCRIBE_ 
commands can be used respectively to publish  and subscribe to a specified channel. In Redis, a channel can have multiple subscribers.
The following Python script shows a basic application using pub/sub with Redis.


```
# publisher.py
import redis
import time

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

channel = 'news'

# Publish messages
for i in range(5):
    message = f"Breaking news #{i}"
    r.publish(channel, message)
    print(f"Published: {message}")
    time.sleep(1)

```

```
#subscriber.py
import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Create pubsub object
pubsub = r.pubsub()

# Subscribe to a channel
pubsub.subscribe('news')

print("Subscribed to 'news'. Waiting for messages...")

# Listen for messages
for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"Received: {message['data'].decode()}")

```



## References

1. <a href="https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern">publisher/subscriber model</a>
2. <a href="https://redis.io/">Redis</a>
3. <a href="https://learn.microsoft.com/en-us/azure/architecture/patterns/publisher-subscriber">Publisher-Subscriber pattern</a>
