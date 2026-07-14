# qubit-note: Set Up 404 Pages with ExpressJS

## Overview

## Set up 404 pages with ExpressJS

In this lesson, you’ll learn how to set up a 404 page. The 404 page will show when a user
tries to visit a page that doesn’t exist.
Setting up a 404 Page
Express has support for * in route paths. This is a special character which matches
anything. This can be used to create a route handler that matches all requests.
The 404 page should be set up just before the call to app.listen. This ensures that
requests for valid pages still get the correct response.

```
app.get('*', (req, res) => {
res.render('404', {
title: '404',
name: 'Andrew Mead',
errorMessage: 'Page not found.'
})
})
```

## References