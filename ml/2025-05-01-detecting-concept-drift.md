# qubit-note: Detecting Concept Drift

## Overview

The note <a href="2025-05-01-detecting-data-drift.md">Detecting Data Drift</a> discusses why we need to cater for data drift and
showed how to do this with <a href="https://github.com/SeldonIO/alibi">alibi</a>. In this note, we will discuss the other core reason
why an ML model in prodcution may fail; namely concept drift.

Concept drift refers to the change in the relationships between the independed and the dependent variables in the model.

## Detecting concept drift

Concept drift occurs when there is a change in the relationship between the independed and the dependent variables in the model.
For example linear regression assumes a relationship of the form

$$y = w_0 + w_1x_1+ \dots + w_{m}x_m + \epsilon $$

However, with time this relationship may not be valid. Concept drift may manifest in any of these forms

- Abruptly:  the model performance suddently drops
- Gradually: the model performance degrades over time
- Periodically: the model is not tuned for example to account for seasonality

So how can we monitor model drift? Although with data drift we can compute the distributions between the train data and the production data, things may not
be so straightforward with concept drift. The reason behind this is that typically in production we lack the ground truth. 
There are several ways we can tackle this. If the labels are simply delayed, we can log the model input and output and once the labels are available
we can trigger a comparing. If the labels are not available, we can use a champion model and compare the predictions of that with the predicitions
coming from the deployed model. This is called a shadow evaluation whereby  a second model (e.g. a previous model) is used in order to compare the two outputs and monitor divergence.
Furthermore, when labels are not available we can use proxy signals and compare with the test set. Proxy signals include

- mean prediction
- histogram of predictions
- % of positive predictions

If the model outputs probabilities or uncertainty estimates track entropy and confidence distribution; a sudden drop indicate a possible problem.
Another approach that we always want to use, is monitoring various business signals:

- Conversion rate
- Claim rate
- Fraud detection rate
- Loss ratio (insurance)

Business signals should always be available and if we detect that these shift then this is a strong drift signal.

All in all, model drift detection in production relies on delayed ground truth for true evaluation, combined with proxy signals 
like prediction distribution shifts, feature drift, and business metrics to detect issues early before labels arrive.

## Summary

## References

1. Andrew P. McMahon, _Machine Learning Engineering with Python_, 2nd Edition, Packt Publications.
2. Chip Huyen, _Designing Machine Learning Systems. An iterative process for production ready applications_, O'Reilly.
