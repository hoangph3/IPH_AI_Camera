import cv2


def draw_line(event, x, y, flags, param):
    global drawing, line_start, line_end, ix, iy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        line_start = (x, y)
        ix, iy = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        line_end = (x, y)
        cv2.line(img, line_start, line_end, (0, 255, 0), 2)
        endpoints.append(((ix, iy), (x, y)))
        cv2.imshow("Draw Line", img)


endpoints = []
save_dir = ""
# Open the video file
# input_video_path = "./testvid/12.mov"
input_video_path = "rtsp://admin:Iph@2024@10.0.0.214:554/ch01.264/0"
cap = cv2.VideoCapture(input_video_path)

# Capture a thumbnail
ret, frame = cap.read()

# Resize the frame to 2560 x 1440 pixels
# target_resolution = (1920, 1080)
# target_resolution = (1280,960)
# frame = cv2.resize(frame, target_resolution)

img = frame.copy()

# Create a window and set the callback function for drawing
cv2.namedWindow("Draw Line")
cv2.setMouseCallback("Draw Line", draw_line)

drawing = False
line_start, line_end = (-1, -1), (-1, -1)

while True:
    cv2.imshow("Draw Line", img)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("c"):  # Press 'c' to apply the drawn line to the video
        break

    elif key == ord("r"):  # Press 'r' to reset the drawn line
        img = frame.copy()
        line_start, line_end = (-1, -1), (-1, -1)

# Create VideoWriter object to save the output video
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# out = cv2.VideoWriter(output_video_path, fourcc, cap.get(5), target_resolution)

# # Apply the drawn line to the entire video
# while True:
#     ret, frame = cap.read()

#     if not ret:
#         break

#     # Resize the frame to the target resolution
#     frame = cv2.resize(frame, target_resolution)

#     # Draw the line on each frame
#     if line_start != (-1, -1) and line_end != (-1, -1):
#         cv2.line(frame, line_start, line_end, (0, 255, 0), 2)

#     # Save the frame to the output video
#     out.write(frame)

#     # Display the frame with the drawn line
#     cv2.imshow("Video with Line", frame)

#     # Break the loop when 'q' key is pressed
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release the VideoCapture and VideoWriter objects
# cap.release()
# out.release()

# # Destroy all OpenCV windows
# cv2.destroyAllWindows()
print("Endpoints:", endpoints)
