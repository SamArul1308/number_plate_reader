import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from vision_msgs.msg import Detection2DArray, Detection2D
from cv_bridge import CvBridge, CvBridgeError
import cv2
import easyocr

class NumberPlateReader(Node):
    def __init__(self):
        super().__init__('ks_number_plate_reader')

        # Subscriptions
        self.image_subscription = self.create_subscription(
            Image,
            '/color/image_raw',
            self.image_callback,
            10
        )

        self.detection_subscription = self.create_subscription(
            Detection2DArray,
            '/detectnet/detections',
            self.detection_callback,
            10
        )

        # Publishers
        self.cropped_image_publisher = self.create_publisher(Image, '/cropped_image', 10)
        self.detected_number_plate_publisher = self.create_publisher(String, '/matched_number_plate', 10)

        # Utilities
        self.bridge = CvBridge()
        self.reader = easyocr.Reader(['en'])  # EasyOCR for text extraction
        self.latest_image = None
        self.latest_detections = []  # Store detections

        # Database of known number plates (placeholder)
        self.known_number_plates = ["MC-RL04", "AB-1234", "XYZ-7890"]

        self.get_logger().info("Number plate reader node started, listening to /color/image_raw...")

    def image_callback(self, msg):
        """Receive and store the latest image from the camera."""
        try:
            self.latest_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            self.get_logger().info("Received image and converted to OpenCV format.")
        except Exception as e:
            self.get_logger().error(f"Image conversion failed: {str(e)}")


    def detection_callback(self, msg):
        """Process incoming detections and crop number plate regions."""
        self.latest_detections = msg.detections
        if self.latest_image is None:
            self.get_logger().warn("No image available for processing.")
            return

        for detection in msg.detections:
            try:
                if detection.results[0].id == 3:  # Class ID 3 for number plates
                    x, y = detection.bbox.center.x, detection.bbox.center.y
                    w, h = detection.bbox.size_x, detection.bbox.size_y

                    # Ensure float values
                    x, y, w, h = float(x), float(y), float(w), float(h)

                    # Crop the region from the latest image
                    x1, y1 = int(x - w / 2), int(y - h / 2)
                    x2, y2 = int(x + w / 2), int(y + h / 2)
                    cropped_image = self.latest_image[y1:y2, x1:x2]

                    # Convert to ROS Image and publish
                    ros_image = self.bridge.cv2_to_imgmsg(cropped_image, encoding='bgr8')
                    self.publish_cropped_image(ros_image)

                    # Perform OCR
                    text = self.extract_text_from_image(cropped_image)
                    if text:
                        match, similarity = self.find_closest_match(text)
                        if similarity >= 0.35:  # Threshold
                            self.publish_matched_text(match)
            except Exception as e:
                self.get_logger().error(f"Failed to process detection: {str(e)}")

    def extract_text_from_image(self, image):
        """Extract text from a cropped number plate image using EasyOCR."""
        try:
            ocr_result = self.reader.readtext(image)
            if ocr_result and len(ocr_result) > 0:
                text = ocr_result[0][1]  # Extract the text part
                self.get_logger().info(f"OCR result: {text}")
                return text
        except Exception as e:
            self.get_logger().error(f"OCR failed: {str(e)}")
        return None

    def find_closest_match(self, detected_text):
        """Find the closest matching text in the predefined database."""
        from difflib import SequenceMatcher

        best_match = None
        highest_similarity = 0.0

        for plate in self.known_number_plates:
            similarity = SequenceMatcher(None, detected_text, plate).ratio()
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = plate

        return best_match, highest_similarity

    def publish_cropped_image(self, image):
        """Publish the cropped image as a ROS Image message."""
        self.cropped_image_publisher.publish(image)
        self.get_logger().info("Published cropped image.")

    def publish_matched_text(self, text):
        """Publish the matched number plate text."""
        msg = String()
        msg.data = text
        self.detected_number_plate_publisher.publish(msg)
        self.get_logger().info(f"Published matched number plate text: {text}.")

def main(args=None):
    rclpy.init(args=args)
    node = NumberPlateReader()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

