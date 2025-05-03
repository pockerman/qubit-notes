# qubit-note: Collection of Training Data

## Overview

Machine learning models in one way or another recognise patterns in data. In order to do so we need
to feed these models with training data so that we are able to tune somehow their parameters.
In this short note, I want to go over some methodologies for collecting training data.
Notice that these are some ideas and not necessarily the only approaches available; for example we could easily
mix any of these as another approach. 


**keywords** machine-learning, data-collection, machine-learning-model-development

## Collection of training data

Training data is of paramount importance every time we want to develop a new ML model. 
This is the case regardless of whether we are training a model from scratch, or using <a href="https://en.wikipedia.org/wiki/Transfer_learning">transfer learning</a> or we simply
<a hre="https://en.wikipedia.org/wiki/Fine-tuning_(deep_learning)">fine-tune</a> the model over the specific cases we have want to model.

There are various ways we can collect training data that I will describe below.

**Pre-existing system data**

If you are lucky enough to work on a system that already collects data that you can utilise for training models that's awesome.
This is probably the first step in your efforts. This does not mean that you won't have to clean or transform the data,
but it's definitely a good start.

**Utilise open source datasets**

In addition to using pre-existing system data, or alternatively, you can utilise available public datasets.
Web platforms such as <a href="https://www.kaggle.com/">Kaggle</a> can provide you with datasets to start your modelling efforts.
Moreover, depending on the task in hand you may be able to utilise models such as ChatGPT for data generation or given that
these models typically are trained over massive datasets you can use these as search engines for finnding data.

**Build the system such that it collects data for you**

In extreme scenarios, you may not be able to find any data that is needed for your modelling task or the data
you collected is simply not enough,assuming that data augmentation and/or synthetic data reached their capacity.
In such scenarios, maybe you want to postpone you modelling attempts and instead roll out a system that collects the
needed data for you. Assuming that you application has some decent traffic you will be able to start your modelling efforts
in a relatively short amount of time. Plus you already have a system in place that collects data for you something that you can utilise
in the future when you go back to the white board in order to improve the model. 
This approach is akin to <a href="https://en.wikipedia.org/wiki/Fake_it_till_you_make_it">fake it unitl you make it</a> mindset.

**Explore GANs**

I find <a href="https://en.wikipedia.org/wiki/Generative_adversarial_network">generative adversarial network</a>, or GAN for short, as a fantastic technique that
we can utilise if we want to expand our dataset. Let's assume that we have a classification problem that deals with three classes/labels.
One of these classes is under-represented. More than likely any model we will train is such a dataset, will fail when it comes to
the under-represented class. Sure we can use weighting to mitigate this but having a proper balanced dataset is probably better.
In this case we can use GANs in order to artificially generate data for the under-represented class. 


Finally, I want to mention the case where we available a significant volume of data but it requires labelling.
There are various ways we can tackle such a scenario from using  human labelers to interatively building models
that do the labelling for us. For example we can start with a small dataset that is labelled manually train a small
model that has some good accuracy, label a few more data points and then train a more ellaborate model and so on.


## References


1. <a href="https://en.wikipedia.org/wiki/Transfer_learning">Transfer learning</a> 
2. <a hre="https://en.wikipedia.org/wiki/Fine-tuning_(deep_learning)">Fine-tuning</a>
3. <a href="https://en.wikipedia.org/wiki/Fake_it_till_you_make_it">Fake it unitl you make it</a>
4. <a href="https://en.wikipedia.org/wiki/Generative_adversarial_network">Generative adversarial network</a>
