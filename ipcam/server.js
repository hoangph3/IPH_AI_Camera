const cv2 = require("opencv4nodejs");
const express = require("express");
const path = require("path");
var cors = require('cors')
var bodyParser = require('body-parser');
var cron = require('node-cron')
const { execSync} = require("child_process")

const fs = require("fs");
const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(cors())
const server = require("http").Server(app);

const io = require("socket.io")(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
    transports: ["websocket", "polling"],
    credentials: true,
  },
  allowEIO3: true,
});

const config = JSON.parse(fs.readFileSync("./env/prod.json", "utf8"));

// Import file
app.use(express.static(__dirname + "/"));

const camera_url = config.camera_url;
const camera = config.camera;
const len = camera.length;
const FramePerSec = 12;

//tracker
var curId = 'cam2';
var change = false;

let isProcessing = false;

app.get(`/cam`, (req, res) => {
  try {
    if (isProcessing) {
      res.sendFile(path.join(__dirname, `index.html`));
      return;
    }

    isProcessing = true;

    var curIndex = camera.indexOf(curId);
    var cap = new cv2.VideoCapture(camera_url[curIndex]);

    const captureFrame = () => {
      if (change === true) {
        console.log("change");
        cap.release();
        execSync("sleep 0.1");
        var curIndex = camera.indexOf(curId);
        cap = new cv2.VideoCapture(camera_url[curIndex]);
        change = false;
      }

      var frame = cap.read();
      if (frame.empty) {
        console.log("No frame captured!");
        try {
          cap.reset();
          console.log("Reset camera success!");
          frame = cap.read();
        } catch (error) {
          console.log("Reset error:", error);
        }
      }

      let image = cv2.imencode(".jpg", frame).toString("base64");
      io.emit(`image`, image);

      if (isProcessing) {
        setTimeout(captureFrame, 1000 / FramePerSec);
      }
    };

    captureFrame();

    res.sendFile(path.join(__dirname, `index.html`));
  } catch (error) {
    console.log(error);
    isProcessing = false;
  }
});

app.post(`/cam`, (req, res) => {
  curId = req.body.camera_id
  change = true

  res.sendStatus(200)
});

server.listen(3030, () => {
  console.log(`server listen on port 3030`);
});
