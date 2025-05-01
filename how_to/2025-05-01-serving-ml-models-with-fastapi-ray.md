# Note: Serving ML Models With FastAPI & Ray


# Overview

In this hands on note I want to show you how to serve an ML model using <a href="https://fastapi.tiangolo.com/">FastAPI</a> 
and <a href="https://docs.ray.io/en/latest/index.html">Ray</a>.
In particular, we will use the former as an access point to our model and the latter to actually scale the serving layer.

For more information see <a href="https://docs.ray.io/en/latest/serve/http-guide.html">Set Up FastAPI and HTTP</a> and 
<a href="https://docs.ray.io/en/latest/serve/index.html">Ray Serve: Scalable and Programmable Serving</a>.


**keywords:** ml-model-serving, Python, Ray, MLOps

## Serving ML models with FastAPI & Ray

Deplpying an ML model to production although not a nuclear physics thing it has its nuances. One of the things
we need to account for is the traffic we  anticipate and create the needed deployments. All these can be quite cumbersome.
Fortunately, Ray, and in particular Ray Serve allows us to easilly deploy our ML models in cluster environment and manages
all the infrastucture for us.

Specifically, Ray Serve is a scalable, framework-agnostic model serving library.
Ray Serve is also well suited for model composition and many model serving, that enables us to build a 
complex inference service consisting of multiple ML models and business logic all in Python code [1].

Below is a toy example that you can easilly extend further to more advanced scenarios.



```
# classifer.py

class DummyModel:
    def predict(self, input: str) -> int:

        if input == "2":
            return 1
        elif input == "3":
            return 2
        return 0

```


```
# main.py
from fastapi import FastAPI
import ray
from ray import serve

from classifier import DummyModel

ray.init()
serve.start()

app = FastAPI(
    title="FastAPI-Ray-Demo",
    summary="Demo showcasing FastAPI with Ray for ML model serving",
    version="0.0.1",
)


@serve.deployment(num_replicas=2, ray_actor_options={"num_cpus": 0.2, "num_gpus": 0})
@serve.ingress(app)
class ClassifierDeployment:

    def __init__(self):
        self.model = DummyModel()

    @app.get("/")
    async def root(self):
        return "Hello, world!"

    @app.post("/model/predict")
    async def root(self, input: str):

        classification = self.model.predict(**{'input': input})
        return classification


ray_app = ClassifierDeployment.bind()

```

Open a terminal and run

```
serve run main:ray_app
```

This should print some messages like the following

```
2025-05-01 15:57:31,595	INFO scripts.py:494 -- Running import path: 'main:ray_app'.
2025-05-01 15:57:32,466	INFO worker.py:1843 -- Started a local Ray instance. View the dashboard at http://127.0.0.1:8265 
INFO 2025-05-01 15:57:33,927 serve 45584 -- Started Serve in namespace "serve".
INFO 2025-05-01 15:57:33,942 serve 45584 -- Connecting to existing Serve app in namespace "serve". New http options will not be applied.
INFO 2025-05-01 15:57:33,945 serve 45584 -- Connecting to existing Serve app in namespace "serve". New http options will not be applied.
(ProxyActor pid=45785) INFO 2025-05-01 15:57:33,882 proxy 192.168.0.129 -- Proxy starting on node e03fc4392b6191208e48a78311f3982431b6ae880904bdebc33b6f85 (HTTP port: 8000).
(ProxyActor pid=45785) INFO 2025-05-01 15:57:33,915 proxy 192.168.0.129 -- Got updated endpoints: {}.
(ServeController pid=45789) INFO 2025-05-01 15:57:33,987 controller 45789 -- Deploying new version of Deployment(name='ClassifierDeployment', app='default') (initial target replicas: 2).
(ProxyActor pid=45785) INFO 2025-05-01 15:57:33,989 proxy 192.168.0.129 -- Got updated endpoints: {Deployment(name='ClassifierDeployment', app='default'): EndpointInfo(route='/', app_is_cross_language=False)}.
(ProxyActor pid=45785) INFO 2025-05-01 15:57:34,022 proxy 192.168.0.129 -- Started <ray.serve._private.router.SharedRouterLongPollClient object at 0x7fe1f54a0e30>.
(ServeController pid=45789) INFO 2025-05-01 15:57:34,090 controller 45789 -- Adding 2 replicas to Deployment(name='ClassifierDeployment', app='default').
INFO 2025-05-01 15:57:35,057 serve 45584 -- Application 'default' is ready at http://127.0.0.1:8000/.
```

If no error has occurred, the we can access the docs offered out of the box from FastAPI at: http://127.0.0.1:8000/docs. You can then test the dummy model with some input.
Some server output is shown below

```
(ServeReplica:default:ClassifierDeployment pid=45792) INFO 2025-05-01 15:57:44,027 default_ClassifierDeployment f4tetqst 7e94b127-a01b-4257-8789-a1dbb3c730d6 -- GET /docs 200 1.2ms
(ServeReplica:default:ClassifierDeployment pid=45787) INFO 2025-05-01 15:57:44,173 default_ClassifierDeployment 5p19vjux 0fbcdfbd-c13b-476d-93b4-117a9d26d0c4 -- GET /openapi.json 200 2.7ms
(ServeReplica:default:ClassifierDeployment pid=45787) INFO 2025-05-01 15:57:49,808 default_ClassifierDeployment 5p19vjux b9eef25a-bac7-48ff-9819-47df2db5082f -- POST /model/predict 200 1.7ms
(ServeReplica:default:ClassifierDeployment pid=45787) INFO 2025-05-01 15:57:55,978 default_ClassifierDeployment 5p19vjux e90a0d47-59d0-4c07-8d92-dca70df3e520 -- POST /model/predict 200 1.5ms
(ServeReplica:default:ClassifierDeployment pid=45792) INFO 2025-05-01 15:57:59,913 default_ClassifierDeployment f4tetqst f03bebd8-4ed7-46b1-877f-ddcef0b5ef9a -- POST /model/predict 200 1.7ms
``` 

In the example above we used 2 replicas. Observe that Ray Serve handled the traffic for us and forwarded the traffic to the two replicas without any input from our side.

## References

1. <a href="https://docs.ray.io/en/latest/serve/index.html">Ray Serve: Scalable and Programmable Serving</a>