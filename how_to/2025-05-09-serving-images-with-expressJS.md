# qubit-note: Serving Images With ExpressJS

## Overview

Often when we work with web applications, we need to serve various assets such as images, CSS files and JavaScript.
In this note, I will shou you how to do this with <a href="https://expressjs.com/">ExpressJS</a>. I
will continue the example from <a href="2025-05-08-hello-expressJS.md">qubit-node: Hello ExpressJS</a>.

Note that the way I am showing in this note, it's not necessarilly the way we want to organise our views.
In a later note I will discuss how to better serve static files with NodeJS.

**keywords:** programming, NodeJS, ExpressJS

## Serving images with ExpressJS

Let's continue the example in <a href="how_to/2025-05-08-hello-expressJS.md">qubit-node: Hello ExpressJS</a> by
adding an endpoint that serves images. I will only add the new code. Create a new directory called _public_.
Within the directory place an image and the following html

```
<!-- index.html -->

<!DOCTYPE html>
<html>
<head>
</head>
<body>
<h1>About</h1>
<img src="/imgs/img.jpeg">
</body>
</html>

```

Add the following code in the ```index.js``` file.

```

...
const path = require('path');
const publicDirectoryPath = path.join(__dirname, './public');

app.use(express.static(publicDirectoryPath));

...

```

Start the NodeJS server using

```
node index.js
```

Navigate to ```http://localhost:3000/``` and you should be able to access the view. 
As I already mentioned in the _Overview_, the way we serve a static file above, it's not necessarilly the way we want to organise our views.
Note <a href="2025-05-10-handle-dynamic-pages-with-expressJS.md">qubit-note: Handle Dynamic Pages with ExpressJS</a> discusses how to
handle dynamic views with ExpressJS

## References

1. <a href="https://expressjs.com/">ExpressJS</a>
