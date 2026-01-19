import cv2
import numpy as np


def capture_image_from_rtsp(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("Error: Unable to open RTSP stream.")
        return None

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Error: Failed to capture frame from RTSP stream.")
        return None

    return frame


def draw_line_on_image(
    image, line_coordinates, line_color=(0, 255, 0), line_thickness=2
):
    x1, y1, x2, y2 = line_coordinates
    image_with_line = np.copy(image)
    cv2.line(image_with_line, (x1, y1), (x2, y2), line_color, line_thickness)
    return image_with_line


def save_image_with_line(image_with_line, output_path):
    cv2.imwrite(output_path, image_with_line)
    print(f"Image with line saved to: {output_path}")


# RTSP stream URL
rtsp_url = "rtsp://admin:Iph@2024@10.0.0.213:554/ch01.264/0"

# Line coordinates (replace with your actual coordinates)
line_coordinates = (394, 714, 1470, 652)

# Capture image from RTSP stream
image = capture_image_from_rtsp(rtsp_url)

if image is not None:
    # Draw line on the captured image
    image_with_line = draw_line_on_image(image, line_coordinates)

    # Save the image with the line
    output_path = "/home/kotora/Workspaces/Tracking-ReID/reid/tests/thumbnail/system_thumbnail/cam13.jpg"
    save_image_with_line(image_with_line, output_path)
