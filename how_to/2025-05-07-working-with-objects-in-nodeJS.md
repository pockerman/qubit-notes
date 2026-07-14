# qubit-note: Working With Objects in NodeJS


## Overview


## Working With Objects in NodeJS

ES6 has done wonders making JavaScript easier to use. In this lesson, you’ll explore a
couple of features that make it easier to work with objects.
Property Shorthand
The property shorthand makes it easier to define properties when creating a new object. It
provides a shortcut for defining a property whose value comes from a variable of the same
name. You can see this in the example below where a user object is created. The name
property gets its value from a variable also called name.


const name = 'Andrew'
const userAge = 27
const user = {
name: name,
age: userAge,
location: 'Philadelphia'
}
The shorthand allows you to remove the colon and the reference to the variable. When
JavaScript sees this, it’ll get the property value from the variable with the same name. The
example below uses the property shorthand to define name on the user object.
const name = 'Andrew'
const userAge = 27
const user = {
name,
age: userAge,
location: 'Philadelphia'
}


console.log(user)
Object Destructuring
The second ES6 feature is object destructuring. Object destructuring gives you a syntax
for pulling properties off of objects and into standalone variables. This is useful when
working with the same object properties throughout your code. Instead of writing
user.name a dozen times, you could destructure the property into a name variable.
You can see an example of this below.

const user = {
name: 'Andrew',
age: 27,
location: 'Philadelphia'
}
// The line below uses destructuring
const { age, location:address } = user
console.log(age)
console.log(address)
user is destructured on line 8 above. The age property has been destructured and stored
in age. The location property has also been destructured and stored in address.
Destructuring Function Arguments
Destructuring works with function parameters as well. If an object is passed into a function,
it can be destructured inside the function definition. You can see this in the transaction
function below. The function accepts an object as its second argument. The label and
stock properties have both been destructured into standalone variables that become
available in the function.


const product = {
label: 'Red notebook',
price: 3,
stock: 201,
salePrice: undefined,
rating: 4.2
}
const transaction = (type, { label, stock }) => {
console.log(type, label, stock)
}
transaction('order', product)



## References