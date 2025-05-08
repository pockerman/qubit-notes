# qubit-node: Hello ExpressJS

## Overview

In this short note, I show how to use <a href="https://expressjs.com/">Express</a> to create a web server.

**keywords:** programming, NodeJS, ExpressJS

## Hello ExpressJS

In this we will use ExpressJS to create a minimalistic web server. First
we need to create a project and initalise ```npm```

```
mkdir hello-expressjs
cd hello-expressjs
npm init
```

Install ExpressJS

```
npm i express
```

Create an ```index.js``` file and add the following code in it.

```
const express = require('express');

// inquire the server name
const os  = require('os');

// create the app: Now, app can be used to set up the server. Let’s start by showing a message when
// someone visits the home page at localhost:3000
const app = express();


app.get('', (req, res) => {
	res.send('Hello Express App');
});

app.get('/server-name', (req, res) => {
	res.send({name: os.hostname()});
});


app.listen(3000, () => {

	console.log('Server is listening on port 3000');

});

```

## References

1. <a href="https://expressjs.com/">Express</a>