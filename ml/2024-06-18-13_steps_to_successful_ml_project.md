# Note: 13 + 1 Steps For a Successful ML Project


## Overview

In this rather lengthy note I would like to point out 13 + 1 steps that I believe that if followed
will lead to a successful machine learning project. However, let me point out that when I say
successful ML project I mean that of developing a model that can be used in your product or as a product.
Thus, I don't mean developing a successful ML-based product. Although interelated these two, for obvious reasons,
having a successful ML model does not necessarily imply a successful product.


The steps are outlined below:

1. Understand the problem we are trying to solve and the context that the solution should be applied.
2. Establish the success metrics
3. Get the data early
4. Clean the data 
5. Know your modelling options (including baselines)
6. Allow time for experimentation
7. Version the data
8. Version the models
9. Track the experiments
10. Test the infrastructure
11. Automate
12. Communicate results to domain experts
13. Iterate for optimization
14. Think about model deployment

Let me describe these steps one by one. Note that this is not necessarilly a linear process. That is once at step 3 it does not
mean you don't go back to step 1. Also, some steps may be taken simultaneously check for instance step 1, step 3 and step 4.
Some steps however may  not. For example it does not make much sense throwing irrelevant data to a possibly irrelevant model just
because you want to speed up the process.


**keywords** machine-learning, project-management, machine-learning-model-development

## 13 +1 steps for a successful ML project

Let's dive a bit more on the steps presented in the _Overview_ section.

#### Step 1. Understand the problem we are trying to solve and the context that the solution should be applied.

Understanding the problem that you are trying to solve is a prerequisite  for solving it. This is not true just for a machine learning
model but probably for every problem one is trying to solve. At this step
we gather as much information as possible about the problem and also get familiar with the language used in the
domain of interest. This step involves a lot of interaction with domain experts and a lot of background research
of how others attempted to solve the same or similar problems. In addition, we need to understand the context within which our solution
will operate. This dictates, among other things, the performance of the model in terms of accuracy, deployment and latency.


#### Step 2: Establish the success metrics

Establishing success metrics allows us to take a more educated approach when deciding upon whether the approach should be followed or another approach should be established. 
In addition, success metrics allow us to summarize results more easily and more compactly.
Obviously, if we don't understand the problem we are trying to solve as well as the context that a solution
is sought, establishing meaningful metrics may not be possible. 


#### Step 3: Get the data early.

Getting access to the data as early as possible has several advanatges. 
First, it avoids unexpected access problems e.g. security clearance is required which may take time to acquire and thus completely derail the project in terms of time budgeting.
Second, it may be helpful towards understanding the problem better as the data will represent a subset of the domain we are trying to understand and hence model. Third, it will give us hints about how much time the data prepocessing step development will require as well as what technologies we may need, e.g. SQL vs NoSQL databases, and what sort of cleaning we may have to do. 
It will also give us an idea of the provisions we need to do in terms of infrastructure e.g. distributed machines or GPUs or both.

#### Step 4: Clean the data

Any data model or data-based product should be built on clean data i.e. outliers removed, values scaled if needed, missing values replaced e.t.c. 
This is becuase of the simple rule: garbage in garbage out which holds for any modelling/simulation effort. 
How much clean the data should be or if the outliers should be removed depends to a large extent on what you are trying to model, 
i.e. step 1, and the model we are adopting. Algorithms have their own pros and cons that you should be aware when putting them on the test.
This step is also related to Step 5 below.


#### Step 5: Know your modelling options

Already mentioned in Step 4, you need to know the pros and cons of the algorithms you decide to put into testing. Hyperparameters, restrictions e.g.
only linear relationships can be modelled, computing resources e.g. time and memory, assumptions about the data being made, error metrics that can be used. All these play their role in the success or failure of the model when applied to your use case. Prefer simpler models to complex ones in order to avoid overfitting and favour interpretability of the results.
Also you need to consider baselines; i.e. simple solutions that are, very, quick to develop and provide some decent results.
There is not point developing complex models only to find out that a simple averaging would have done the trick.


#### Step 6: Allow time for experimentation

<a href="https://en.wikipedia.org/wiki/All_models_are_wrong">All models are wrong some are useful</a>. 
Given this we need to be able to explore the solution space as much as possible in order to deliver
an as best model as possible. Thus it is essential to factor in the available time budget the time needed to explore alternative models.
I am not talking here about optimizing an existing model but a different model altogether e.g logistic regression vs Knn when it comes 
to classification. This is an essential element of your model development process and knowing pros and cons of each model and by understanding
what you are trying to solve will help you make better educated decisions as to which alternatives to explore. 


#### Step 7: Version the data

Versioning data is one thing that differentiates ML engineering with casual software engineering. It is essential that we version
the data sets and maintain a catalogue of features associated with each and every data set. 
This is required in order to be able to reproduce your results or train a new model on the same data that we used to train the existing models. 
There are various products out there that they can help in this goal e.g. <a href="https://dvc.org/"DVC</a> and <a href="https://mlflow.org/"MLflow</a>.

#### Step 8: Version the models

Versioning the  models we use goes hand in hand with versioning the data. 
Models will typically be retrained over new datasets and therefore being able to track changes that have occured in the model becomes evident. 
This will be useful in cases where you would like to roll back to an older version of the model.

#### Step 9: Track the experiments

Numerical simulation and data-based models have one thing in common; they require a lot of experimenation on the same model. Consider for example
a deep neural network and the number of choices you have to make before even trying to run the training process; 
learning rate, regularization, batch size, weight decay, loss function, train on CPU or GPU e.t.c. 
Surely not all of these parameters will give you substantial improvements however it illustrates the point. 
Thus it is essential that you track the parameters that affect the output of the training process. 
<a href="https://mlflow.org/"MLflow</a> is a tool you can use for this amongst many others.

#### Step 10: Test the infrastructure

Training pipelines is software and as such they  should be tested. 
You don't want to think that you were using ResNet18 model whilst you were actually using a ResNet50 for example. 
It is a good software practice to test your implementation. <a herf="https://en.wikipedia.org/wiki/Test-driven_development">Test driven development</a> or TDD, is an approach you can utilise.
In this approach, before implementing any functionality you develop its test. Obviously the test fails intially as there is no functionality and thus you go along
and develop it. This loop continues until all tests are green. This approach has the following two advantages

- You have tests for you infrastructure at the end of the process
- Helps you to better grasp what you want to do

The typical behaviour is to add tests after the infrastructure has been established. 
This is mostly development driven testsing DDT and has the following disadvantages

- It entails an at least difficult to test functionality as the latter was not developed with testability in mind.
- It requires to revisit your requirements.
- It leaves a window of non tested code open until the tests are integrated. I am not sure if you really want this.
- You may have to alter your code in order to test it (point 1 above) which leads to new bugs (most likely).

#### Step 11: Automate

Automation has several advantages

- Replay results
- Save time
- Less error prone

On the other hand, you may require some extra time in order to gain the new skills needed. But given that CI/CD has overtaken ML engineering as much as traditional software engineering, it means that it is a good practice that you should strive to follow. This is particularly true if your training pipeline involves a number of steps.
And it is kind of a neccessity in order to train your model on the cloud or a dedicated cluster.


#### Step 12: Communicate your results to domain experts

As an ML engineer or a data scientist you may not neccessarilly have the knowledge required in order to assess the quality of a model (see step 1). This will be true in the initial stages of the project or if you haven't worked on that particular domain before. Regardless of the reason, you should communicate the results to domain experts. 
They have the know how of the field and therefore can assess better whether the results make sense and hopeffully help you in which direction to take. 
Don't neglect this step as depending on the complexity of the field, may dictate your success or failure.

#### Step 13: Iterate for optimization

If you think you are done you are wrong. Engineering in general involves a lot of iterations and ML/data science is not an exception. I would say
that is even more pertinent to that field given the fact that you don't necessarilyly work with closed form solutions or establihed models.
Iteration therefore has to happen in order to improve the outcomes of the process. That's why having metrics established is an important step.
Notice also that iteration should occur in various degreess in every step preseneted above. 
Revising and reassessing is the only way to improve any human made process.


#### Step 14: Think about model deployment

Ok we developed a really great model with some fantastically looking metrics only to find out that its requirements in terms of infrastructure
cannot be satisified. This is not necessarilly the best thing so we need to consider up front how the model will be deployed.
This is not the first thing we need to do but as the modeling efforts converge to a few models we would like to use, we need
to start thinking how the selected models will be integrated into our system.


## References

1. <a href="https://en.wikipedia.org/wiki/All_models_are_wrong">All models are wrong some are useful</a>
2. <a href="https://dvc.org/"DVC</a> 
3. <a href="https://mlflow.org/"MLflow</a>
4. <a herf="https://en.wikipedia.org/wiki/Test-driven_development">Test driven development</a>


