# qubit-note: Detecting Concept Drift

## Overview

<a href="2025-05-01-detecting-data-drift.md">qubit-note: Detecting Data Drift</a> discussed why we need to cater for data drift and
showed how to do this with <a href="https://github.com/SeldonIO/alibi">alibi</a>. In this note, I discuss the other core reason
why an ML model in prodcution may fail namely concept drift.

Concept drift refers to the change in the relationships between the independed and the dependent variables in the model.

**keywords:** concept-drift, ml-model-monitoring, alibi, alibi-detect, Python


## Detecting concept drift

Concept drift occurs when there is a change in the relationship between the independed and the dependent variables in the model.
For example linear regression assumes a relationship of the form

$$y = w_0 + w_1x_1+ \dots + w_{m}x_m + \epsilon \tag{2}$$

However, with time this relationship may not be valid. Concept drift may manifest in any of these forms

- Abruptly:  the model performance suddently drops
- Gradually: the model performance degrades over time
- Periodically: the model is not tuned for example to account for seasonality

So how can we monitor model drift? Although with data drift we can compute the distributions between the train data and the production data, things may not
be so straightforward with concept drift. The reason behind this is that typically in production we lack the ground truth. Thus we need to have some sort
of labelling process that will assigne correct labels to production data that will enable us to compare against the model predictions. This however can only be done offline.
In addition, we could be computing statistics over the model predicitions. If a statistically significant change is obsrved then this means 
that the input data distribution has shifted. This shift in prediction is not necessarily an indication of an underlying issue, however is worthwhile tracking it.
Finally, we can use simple models as proxies that can hint about the correct label and if a statistically significan discrepancy is observed then we can trigger an alert.

All in all, detecting model drift is trickier than detecting data drift particularly if we want to do this online.
Nevertheless, since our main objective is to be notified that the model is undeperforming, adopting ad-hoc solutions and simplify
models algoside with an offline labelling process can really help towards maintaing a well performing ML model.

## References

1. Andrew P. McMahon, _Machine Learning Engineering with Python_, 2nd Edition, Packt Publications.
2. Chip Huyen, _Designing Machine Learning Systems. An iterative process for production ready applications_, O'Reilly.