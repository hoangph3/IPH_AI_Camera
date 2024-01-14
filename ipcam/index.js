const cv2 = require("opencv4nodejs");
const express = require("express");
const path = require("path");
const request = require("request");
const {
  Worker,
  isMainThread,
  parentPort,
  workerData,
} = require("worker_threads");

const fs = require("fs");
const app = express();
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

// console.log(config.camera);
// Import file
app.use(express.static(__dirname + "/"));

const camera_url = config.camera_url;
const camera = config.camera;
const len = camera.length;

for (let i = 0; i < len; i++) {
  app.get(`/${camera[i]}`, (req, res) => {
    const cap = new cv2.VideoCapture(camera_url[i]);
    const FramePerSec = 20;

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500);
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500);
    setInterval(() => {
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
        // throw new Error('No frame captured!');
      }
      let image = cv2.imencode(".jpg", frame).toString("base64");
      io.emit(`image${i + 1}`, image);
    }, 1000 / FramePerSec);
    res.sendFile(path.join(__dirname, `templates/index${i + 1}.html`));
  });
}

// app.post("/cam", (req, res)=>{
//   let cam = req.camera_id
//   let i = camera.indexOf(cam)

// })
//  app.get("/cam22", (req, res) => {
//    const cap = new cv2.VideoCapture(
//      "rtsp://admin:Iph@2024@10.0.0.201:554/ch01.264/0"
//    );
//    const FramePerSec = 20;

//    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500);
//    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500);
//    setInterval(() => {
//      const frame = cap.read();
//      const image = cv2.imencode(".jpg", frame).toString("base64");
//      io.emit("image22", image);
//    }, 1000 / FramePerSec);
//    res.sendFile(path.join(__dirname, "index2.html"));
//  });

server.listen(3030, () => {
  console.log("server listen on port 3030");
});
