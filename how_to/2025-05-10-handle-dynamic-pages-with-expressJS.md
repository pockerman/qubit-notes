# qubit-note: Handle Dynamic Pages with ExpressJS

## Overview

Only rarely do we want our web pages to be static. <a href="https://expressjs.com/">ExpressJS</a>
supports a number of template engines that we can use to render dynamic web pages.
In this note, I will show use how to use one of them namely <a href="https://handlebarsjs.com/">Handlebars</a>.

I will continue the code from <a href="2025-05-09-serving-images-with-expressJS.md">qubit-note: Serving Images With ExpressJS</a>


## Handle dynamic pages with ExpressJS

The first thing we need to do is to insatll Handlebars in our project

```
npm i hbs
```

In addition, we need to inform the express app the view engine that we are using

```
app.set('view engine', 'hbs');
```

The default location that our views should live for Express is the _views_ directory. 
So create one and then place in it the following file:

```
<!-- index.hbs -->

<!DOCTYPE html>
<html>
<head>
</head>
<body>
<h1>About</h1>
<p>Hello {{name}}</p>
<img src="/imgs/img.jpeg">
</body>
</html>

```

The ```{{name}}``` is a placeholder for a variable that its value will change according to some criteria.
Now lets add another route to the server. 

```
...
app.set('view engine', 'hbs');
...

app.get('/image-name', (req, res) => {
	res.render('index', {name: 'Joe Doe'});
});

```

Run the ```index.js``` script and navigate to ```http://localhost:3000/image-name``` and you should be able to access the view
with the name variable substituted with _Joe Doe_.


## References

1. <a href="https://expressjs.com/">ExpressJS</a>
2. <a href="https://handlebarsjs.com/">Handlebars</a>


