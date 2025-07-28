import cv2
from pyzbar.pyzbar import decode

def test_qr_code_detection():
    # Load the image
    front_image = cv2.imread("front_image.jpg")

    # Convert to grayscale (pyzbar works best this way)
    gray = cv2.cvtColor(front_image, cv2.COLOR_BGR2GRAY)

    ret, preprocessed_image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Decode the QR code
    decoded_objects = decode(preprocessed_image)

    # Check if any QR code was detected
    assert len(decoded_objects) > 0, "No QR code detected in front_image.jpg"
    
    # Optionally, print the data from the QR code
    for obj in decoded_objects:
        print("Decoded data:", obj.data.decode('utf-8'))    

test_qr_code_detection()
