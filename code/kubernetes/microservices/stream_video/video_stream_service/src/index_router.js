const index_router = require('express').Router();


index_router.get('/', (req, res) => {

    res.send('Hello World');

});

module.exports = index_router;