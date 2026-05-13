# qubit-note: ML Series | Machine Learning Project Life Cycle

## Overview

We have discussed several topics related to machine learning. We will refine these are these notes progress.
Before we do so, let's change gears and discuss the steps a machine learning project typically involves.
This is the machine learning life cycle (MLLC) and it is similar to the software development life cycle (SDLC).


## Machine learning project life cycle

In this chapter, you will go through an example project end to end, pretending to be a
recently hired data scientist in a real estate company.1 Here are the main steps you will
go through:
1. Look at the big picture aka frame the problem.
2. Get the data.
3. Discover and visualize the data to gain insights.
4. Prepare the data for Machine Learning algorithms.
5. Select a model and train it.
6. Fine-tune your model.
7. Present your solution.
8. Launch, monitor, and maintain your system.

We will later put these step into an overal desing of a machine learning platform.
Thus, our point of view if mostly from the system design perspective.


### 1. Look at the big picture

When tasked to solve a problem, one of the first steps is to understand the big picture. 
ML-based solutions don't sit in solitude within a system. Instead they are part of bigger workflow.
So we need to be aware of what exactly is the business objective and how does the company 
expect to use and benefit from this model [1].

---
**Why is this important?**

This is important because it will determine how you frame the
problem, what algorithms you will select, what performance measure you will use to
evaluate your model, and how much effort you should spend tweaking it.

---

The next question to ask is what the current solution looks like (if any). It will often
give you a reference performance, as well as insights on how to solve the problem.
Your boss answers that the district housing prices are currently estimated manually
by experts: a team gathers up-to-date information about a district, and when they
cannot get the median housing price, they estimate it using complex rules.

First, you need to frame the problem: 

- Is it supervised? 
- Is it nsupervised? 
- Reinforcement Learning? 
- A NLP solution is required?

Further questions to ask minclude:

- Is it a classification task?
- Is it a regression task? 
- Should you use batch learning or online learning techniques?

#### Select a performance measure

See Concept 9: What are some common loss functions in machine learning?


---
**Remark: Check the Assumptions**

Lastly, it is good practice to list and verify the assumptions that were made so far (by
you or others); this can catch serious issues early on. For example, the district prices
that your system outputs are going to be fed into a downstream Machine Learning
system, and we assume that these prices are going to be used as such. But what if the
downstream system actually converts the prices into categories (e.g., “cheap,”
“medium,” or “expensive”) and then uses those categories instead of the prices them‐
selves? In this case, getting the price perfectly right is not important at all; your sys‐
tem just needs to get the category right. If that’s so, then the problem should have
been framed as a classification task, not a regression task. You don’t want to find this
out after working on a regression system for months.
Fortunately, after talking with the team in charge of the downstream system, you are
confident that they do indeed need the actual prices, not just categories. Great! You’re
all set, the lights are green, and you can start coding now!

---

### 2. Get the data

See also <a href="2025-04-24-collection-of-training-data.md">qubit-note: ML Series | Collection of Training Data</a>.


## References

1. Aurelien Geron, _Hands On Machine Learning with Scikit-Learn and TensorFlow_, O'Reilly