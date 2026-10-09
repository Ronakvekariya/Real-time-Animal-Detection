import cv2
import time
from imutils.video import FPS
from imutils.video import WebcamVideoStream
import imutils
import datetime
from threading import Thread
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt
import json , socket , os

model  = YOLO("./best.pt")

class FPS:
	def __init__(self):
		# store the start time, end time, and total number of frames
		# that were examined between the start and end intervals
		self._start = 0
		self._end = 0
		self._numFrames = 0
	def start(self):
		# start the timer
		self._start = datetime.datetime.now()
		return self
	def stop(self):
		# stop the timer
		self._end = datetime.datetime.now()
	def update(self):
		# increment the total number of frames examined during the
		# start and end intervals
		self._numFrames += 1
	def elapsed(self):
		# return the total number of seconds between the start and
		# end interval
		return (self._end - self._start).total_seconds()
	def fps(self):
		# compute the (approximate) frames per second
		print("number of frame processsed is ", self._numFrames)
		return self._numFrames / self.elapsed()


class WebcamVideoStream:
    def __init__(self, src=0):
        # Initialize the video camera stream
        self.stream = cv2.VideoCapture(src)
        
        # Set the desired frame width and height to 416x416
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 416)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 416)

        # Read the first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

        # Initialize the variable used to indicate if the thread should be stopped
        self.stopped = False

    def start(self):
        # Start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # Keep looping infinitely until the thread is stopped
        while True:
            # If the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # Otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # Return the frame most recently read
        return self.frame

    def stop(self):
        # Indicate that the thread should be stopped
        self.stopped = True


# created a *threaded* video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")
vs = WebcamVideoStream(src=0).start()
fps = FPS().start()

json_file_path = "./records.json"

if os.path.exists(json_file_path) and os.path.getsize(json_file_path) > 0:
    with open(json_file_path , 'r') as f:
        detection_data = json.load(f)
else:
    detection_data = []
    

def send_data(entry):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Replace with the receiving Raspberry Pi's actual IP address
        client_socket.connect((socket.gethostname(), 8080))
        json_data = json.dumps(entry)
        client_socket.send(json_data.encode('utf-8'))
        client_socket.close()
        print("Data sent successfully.")
    except Exception as e:
        print(f"Failed to send data: {e}")


flag = 0
predictions = []
while True:
    # Grab the frame from the threaded video stream
    frame = vs.read()
    
    # Check if the frame is valid
    if frame is None or frame.size == 0:
        print("Failed to grab frame")
        break
    
    cv2.imshow("yolo object detection" , frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('s'):
        print("the button has been cllicked")
        
        
        # Perform object detection using the YOLO model
        results = model(frame)  # Directly pass the frame to the YOLO
        
        # Check if results contain data
        if len(results) > 0:
            r = results[0]  # Get the first result
            class_ids = r.boxes.cls.cpu().numpy()  # Convert to numpy for easier handling    SAa
            confidences = r.boxes.conf.cpu().numpy()  # Convert to numpy
            
            # Get class names and confidences
            class_names = [r.names[int(cls)] for cls in class_ids]
            class_conf_pairs = list(zip(class_names, confidences))
            top_5_predictions = sorted(class_conf_pairs, key=lambda x: x[1], reverse=True)[:5]

            # Print and filter the top 5 predictions
            print("Top 5 Predictions:")
            for class_name, confidence in top_5_predictions:
                print(f"Class: {class_name}, Confidence: {confidence}")
                flag = 1
                predictions.append(class_name)

            if len(predictions) > 0:
                print(predictions)
                # Prepare data to append
                data = {
                    "raspberry_pi_id": "RPI_12345",
                    "raspberry_pi_ip": "192.168.1.31", 
                    "class_of_animal": f"{predictions}",
                    "time_stamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "location": "testing"
                }

                # Append data to in-memory list
                detection_data.append(data)
                print(f"Data appended in memory: {data}")

                send_data(data)
                predictions = []
                
                # Write all data to the JSON file
                with open(json_file_path, 'w') as f:
                    json.dump(detection_data, f, indent=4)

                print(f"All data written to {json_file_path}")
            else:
                print("No enough confidence in detection")
            # Display the frame
    
            annoated_frame = results[0].plot()
            cv2.imshow("Live Capture (Threaded)",annoated_frame)
            cv2.imwrite("/home/ronak/Downloads/detected_photoes/" +  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ".jpg" , annoated_frame )
    # Update the FPS counter
    fps.update()

    # Press 'q' to exit the loop
    if  key == ord('q'):
        break
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
