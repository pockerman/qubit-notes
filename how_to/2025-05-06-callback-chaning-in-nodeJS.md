# qubit-note: Callback Chaining in NodeJS


## Overview

In this note I want to discuss how to chain callbacks when using NodeJS.
This note however is not meant to cover how to work with the ```async``` module.

**keywords:** programming, NodeJS, async

## Callback chaining in NodeJS

Very often when working with code we need to use the results of one operation as the input to another. 
The following script shows how to do this when working with NodeJS.

```
// index.js

const show_message = (error, message) => {
    
    if(error){
        console.log('There is an error', error);
        return null;
    }
    else{
        console.log(message);
        return "this is a new message";
    }

}
const speak = (error, message, callback) => {

    if(callback === null){
        console.log("You need to specify a callback");
        return;
    }

    new_message = callback(error, message);

    if(new_message){
        console.log(new_message);
    }
   
}   

speak(null, null, null);
speak(null, "message 1", show_message);
speak("this is error", null, show_message);

```

Run the script using

```
node index.js
```

It produces the following output

```
You need to specify a callback
message 1
this is a new message
There is an error this is error
```

This is nothing more than providing a function as a parameter to another function call. Many languages, e.g. Python provide this
functionality. NodeJS also provides the ```async``` module, check [1] on how the use it.

## References

1. <a href="https://www.geeksforgeeks.org/what-is-chaining-in-node-js/">What is Chaining in Node.js?</a> 