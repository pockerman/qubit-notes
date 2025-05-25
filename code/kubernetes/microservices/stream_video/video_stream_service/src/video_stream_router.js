const path = require('path');
const fs = require('fs');
const video_stream_router = require('express').Router();


video_stream_router.get('/', async (req, res) => {


    const videoPath = path.join(__dirname, '../videos/vid_1.mp4');
    //const  videoPath = "../videos/vid_1.mp4";
    const stats = await fs.promises.stat(videoPath);

    res.writeHead(200, {

        "Content-Length": stats.size,
        "Content-Type": "video/mp4",

    });

    fs.createReadStream(videoPath).pipe(res);

})

module.exports = video_stream_router;