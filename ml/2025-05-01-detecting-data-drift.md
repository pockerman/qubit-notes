# qubit-note: Detecting Data Drift

## Overview

When a model is deployed into production it exhibit a performance drop. This is despite the efforts excercised by the data scientists.
This performace drop can be attributed to a variety of reasons. This is called model drift and we split this into two main categories [1,2]:

- Data drift
- Concept drift

In this note I want talk about data drift namely what it is and how to detect it in an ML system.

**keywords:** data-drift, ml-model-monitoring, alibi, alibi-detect, Python

## Detecting Data Drift

Let's start with by trying to give a definition of what is data drift. Machine learning models, in one way or another,
use features extracted from the training data in order to make predictions. Data drift refers to the change of the
statistical properties of the data that the models sees when deployed compared to the properties of the training data.
As an example, consider a model trained to recommend excercises based on the age and weight of the user.
If the model was trained on data that the weight feature  was in the range of say 65kg to 91kg, users that
fall outside this range will automatically cause data drift.

Given that when a model is dployed, we have limited to no control over the data it is passed, it is essential that we are
able to detect the drift betweeen the production data and the train data so that we are able to act timely.

----
**Remark**

It is true that we can use various mechanisms in order to prevent data not suitable for the model to go through
our inference pipeline. There are several downsides of these approaches; may increase the latency of our application to 
respond, may be as expensive as running the inference pipeline. They also add <a href="https://en.wikipedia.org/wiki/Technical_debt">technical debt</a>.

----


Data drift may have different sources. 
For example, it may not necessarilly occur because the incoming data was not foresaw as possible input, But because
the way we sampled the training data in order to develop the model was inappropriate altogether.
Another reason is seasonality; meaning variations in the input data that is attributed purely to the period of the year the
model is queried. For example you need to account for seasonality of ice-cream sales as it is natural to have quite large variations
depending on whether you are looking into winter or summer time. Another reason is that both training and inference pipelines may have bugs, just like
any other piece of software.

Another type of drift in the category of data drift is the so called target drift i.e. there is a change in how the outcomes
are distributed. Typically, we can address this type of drift by retraining the model or by adjusting the inference pipelines
to any data schema changes and/or new classes.

In general, we can automate the training process such that a retraining job is triggered every time data drift is detected.
Having said this ler's see  a toy example how to data drift detection using <a href="https://github.com/SeldonIO/alibi">alibi</a>.
Once very common way to detect data drift is to somehow compare, e.g. using the <a href="https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test">Kolmogorov-Smirnov test</a>, the distributions of the
train data and the input data. If these are statistically different, then  we claim that data drif has occurred.


### Detecting data drift

Now that we have a conceptual understading of what data drift is, let's see how we can detect it. 
We will use a toy example for this taken from [1].
We will use the <a href="https://github.com/SeldonIO/alibi">alibi</a> Python package for this.
```alibi``` is an open-source library written in Python, aimed at machine learning model inspection and interpretation. You can install it via pip:

```
pip install alibi
pip install alibi-detect
```


```
# Tabular detector class: just a wrapper to alibi.TabularDrift

from typing import Any
from alibi_detect.cd import TabularDrift


class TabularDataDriftDetector:

    def __init__(self, p_value: float, x_ref: Any) -> None:
        self.detector = TabularDrift(x_ref=x_ref, p_val=p_value)

    def detect_drift(self, x: Any) -> str:
        preds = self.detector.predict(x)
        labels = ['No', 'Yes']
        return labels[preds['data']['is_drift']]


from collections import namedtuple
import numpy as np
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from src.mlops.tabular_data_drift_detector import TabularDataDriftDetector

DS = namedtuple(typename='DS',
                field_names=['x_ref', 'x_test', 'y_ref', 'y_test'])


def get_data() -> DS:
    wine_ds = load_wine()
    x, y = wine_ds.data, wine_ds.target

    x_ref, x_test, y_ref, y_test = train_test_split(x, y,
                                                    test_size=0.3,
                                                    random_state=42)

    return DS(x_ref, x_test, y_ref, y_test)


def test_with_no_drift():
    data = get_data()
    detector = TabularDataDriftDetector(x_ref=data.x_ref,
                                        p_value=.05)

    is_drift = detector.detect_drift(x=data.x_test)
    assert is_drift == 'No'


def test_with_drift():
    data = get_data()
    detector = TabularDataDriftDetector(x_ref=data.x_ref,
                                        p_value=.05)

    is_drift = detector.detect_drift(x=2.1*data.x_test)
    assert is_drift == 'Yes'

```

## References

1. Andrew P. McMahon, _Machine Learning Engineering with Python_, 2nd Edition, Packt Publications.
2. Chip Huyen, _Designing Machine Learning Systems. An iterative process for production ready applications_, O'Reilly