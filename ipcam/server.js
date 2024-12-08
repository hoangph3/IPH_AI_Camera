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

// Load a placeholder error image (base64 encoded)
const errorImage = fs.readFileSync("./assets/error.jpg").toString("base64");

const attemptCapture = async (url, retries = 5, delay = 1000) => {
  try {
    console.log(`Attempting to connect to: ${url}`);
    let cap = new cv2.VideoCapture(url);

    // Test if the capture object is valid by reading a frame
    let frame = cap.read();
    if (frame.empty) {
      throw new Error("Failed to read initial frame. Camera may not be accessible.");
    }

    console.log("VideoCapture successfully opened.");
    return cap; // Successfully created capture
  } catch (error) {
    const systemError = error.message || "Unknown error occurred";
    console.log(`Error opening video capture: ${systemError}`);

    if (retries > 0) {
      console.log(`Retrying in ${delay / 1000} seconds... (${retries} attempts left)`);
      await sleep(delay); // Wait before retrying
      return attemptCapture(url, retries - 1, delay);
    } else {
      console.error(`All retries failed. Last error: ${systemError}`);
      return null; // Explicitly return null after all retries
    }
  }
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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

    const captureFrame = async () => {
      if (change === true) {
        console.log("Camera change requested.");
        cap.release();
        await sleep(100); // Short delay for releasing resources
        const curIndex = camera.indexOf(curId);
        const url = camera_url[curIndex];
        cap = await attemptCapture(url);

        change = false;
      }

      // If `cap` is null, emit the error image
      if (!cap) {
        console.log("Emitting error image due to capture failure.");
        io.emit("image", errorImage);
        setTimeout(captureFrame, 1000 / FramePerSec); // Retry in the next frame
        return;
      }

      const frame = cap.read();
      if (frame.empty) {
        console.log("No frame captured! Emitting error image.");
        io.emit("image", errorImage);
        setTimeout(captureFrame, 1000 / FramePerSec); // Retry in the next frame
        return;
      }

      const image = cv2.imencode(".jpg", frame).toString("base64");
      io.emit("image", image);

      if (isProcessing) {
        setTimeout(captureFrame, 1000 / FramePerSec);
      }
    };

    captureFrame();

    res.sendFile(path.join(__dirname, `index.html`));
  } catch (error) {
    console.log("Error in GET /cam route:", error.message);
    res.status(500).send(`Failed to start camera stream. Error: ${error.message}`);
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
