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

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const attemptCapture = async (url, retries = 3, delay = 1000) => {
  try {
    let cap = new cv2.VideoCapture(url);
    let frame = cap.read();
    if (frame.empty) {
      throw new Error("Failed to read initial frame. Camera may not be accessible.");
    }
    return cap;
  } catch (error) {
    console.log(`Error opening video capture: ${error.message}`);
    if (retries > 0) {
      console.log(`Retrying in ${delay / 1000} seconds... (${retries} attempts left)`);
      await sleep(delay); // Wait before retrying
      return attemptCapture(url, retries - 1, delay);
    } else {
      console.log("All retries failed.");
      return null;
    }
  }
};

app.get(`/cam`, async (req, res) => {
  try {
    if (isProcessing) {
      res.sendFile(path.join(__dirname, `index.html`));
      return;
    }

    isProcessing = true;

    const curIndex = camera.indexOf(curId);
    const url = camera_url[curIndex];
    let cap = await attemptCapture(url);

    if (!cap) {
      isProcessing = false;
      res.status(500).send("Failed to open video capture.");
      return;
    }

    const captureFrame = async () => {
      if (change === true) {
        console.log("change");
        cap.release();
        await sleep(100); // Short delay for releasing resources
        const curIndex = camera.indexOf(curId);
        const url = camera_url[curIndex];
        cap = await attemptCapture(url);
        change = false;
      }

      const frame = cap.read();
      if (frame.empty) {
        console.log("No frame captured!");
        try {
          cap.reset();
          console.log("Reset camera success!");
        } catch (error) {
          console.log("Reset error:", error);
        }
      }

      const image = cv2.imencode(".jpg", frame).toString("base64");
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
