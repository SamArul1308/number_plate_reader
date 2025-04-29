#  Number Plate Reader

The Number Plate Reader node utilizes EasyOCR for recognizing text from number plates, whose bounding boxes are given by detectnet, captured by a camera feed and compares it against a database to find matches. If a match is found, it publishes the matching result to a specified ROS2 topic. Number plate recognition can be used in multiple scenarios such as surveillance, speed check cameras. The component is implemented for sending information to the environment mapper that a vehicle with a number plate of a certain id has ben spotted by the camera. 

This component is written to satisfy the Module 4 Criteria 7 (Vehicle detects the vehicle in front and its number plate) User Story 1

## M4.7.1 - Detection of the number plate in front
As the detectnet, I want to detect and recognise the number plates on the vehicle in the front from the images captured by the camera, so that the vehicle on the front can be recognized.

### Acceptance Criteria:
1. [x] Detectnet must be subscribed to a topic that publishes the camera images.
2. [x] Detectnet must be trained to detect the number plates on the vehicles.
3. [x] Detectnet must publish the coordinates of the bounding box of the number plate.
4. [x] The Number Plate Reader component must receive the bounding box coordinates and extract the number plate from the image.
5. [x] The Number Plate Reader must match the detected number plate against a database and return the matched number plate.

## Author
Sam Schwartz Arul Agastus
## Input

|       | Topic | Message   | Description                               |
|-------|-------|-----------|-------------------------------------------|
| Input |/color/image_raw| [sensor_msgs/msg/Image.msg](https://github.com/ros2/common_interfaces/blob/rolling/sensor_msgs/msg/Image.msg)  | Image frames captured from a camera feed |
| Input |/detectnet/detections| [vision_msgs/msg/Detection2DArray](http://docs.ros.org/en/lunar/api/vision_msgs/html/msg/Detection2D.html)  | Detection results from the detectnet model, which includes information on bounding boxes and the class of each detected object |

## Processing

### Usage of detection msg 
- The detection msg has to be used to filter the detection with class id x03 which corresponds to number__plate and extract the bounding box information.

### Image Cropping
- Image is cropped as per the bounding box with the image from camera '/color/image_raw` for the class id x03 which corresponds to number__plate and the 

### OCR Detection
- The cropped imnage is taken and with the usage of OpenCV and [EasyOCR](https://github.com/JaidedAI/EasyOCR) the text in the image frames are detected. 

### Text Matching
- Compares detected text with a predefined list of number plates in the database.
- Uses the SequenceMatcher from the `difflib` library to determine the closest match by similarity ratio.

### Matching Threshold
- If the similarity ratio of the detected text against the database exceeds a threshold (e.g., 0.35), it considers the text a match.
- Publishes the matched number plate to the `detected_number_plate` topic.

## Output

|        | Topic | Message | Description                     |
|--------|-------|---------|---------------------------------|
| Output |/detected_number_plate| [std_msgs/msg/String.msg](https://github.com/ros2/common_interfaces/blob/rolling/std_msgs/msg/String.msg) | Publishes the recognised number plate|
| Output (Only for visualization) |/cropped_image| [sensor_msgs/msg/Image.msg](https://github.com/ros2/common_interfaces/blob/rolling/sensor_msgs/msg/Image.msg)  | Images cropped to the number plate coordinates from Detection message|


