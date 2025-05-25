const express = require('express');
const mongodb = require('mongodb');

// routers
const index_router = require('./index_router');
const video_stream_router = require('./video_stream_router');


if(!process.env.PORT){
    throw new Error('PORT is not defined');
}

// config for the app
const PORT = process.env.PORT;
const DBHOST = process.env.DBHOST;
const DBNAME = process.env.DBNAME;


const app = express();

app.use('/', index_router);
app.use('/video-stream', video_stream_router);


app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});



