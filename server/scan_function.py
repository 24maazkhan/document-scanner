import cv2
import numpy as np
from imutils.perspective import four_point_transform
import pytesseract
import os

# Tesseract OCR Path
pytesseract.pytesseract.tesseract_cmd = r'E:\Programs\Tesseract-OCR\tesseract.exe'

# SCAN SETTINGS
WIDTH, HEIGHT = 800, 600

# IMAGE PROCESSING
def image_processing(image): # Grayscale conversion
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    _, threshold = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY) # Applies Threshold for GrayScale
    return threshold

# SCAN DETECTION
def scan_detection(image):
    document_contour = np.array([[0, 0], [WIDTH, 0], [WIDTH, HEIGHT], [0, HEIGHT]]) # Sets document default contour
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # convert to grayscale
    blur = cv2.GaussianBlur(gray, (5,5), 0) # smooths image
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) # converts image to black and white using Otsu's method

    cnts, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) # finds all contours in image
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True) # sorts contours by area

    max_area = 0
    for c in cnts: # Biggest 4 point shape is selected as document contour
        area = cv2.contourArea(c)
        if area > 1000:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.015 * peri, True)
            if area > max_area and len(approx) == 4:
                document_contour = approx
                max_area = area

    return document_contour.reshape(4,2)

# MAIN FUNCTION
def process_file(input_path, output_type='scan'):
    #  Args:
    #  input_path (str): path to .jpg
    #  output_type (str): 'scan' or 'text'
    #  Returns:
    #  bytes (scan) or str (text)

    if not os.path.exists(input_path): # verifies if file exists
        raise FileNotFoundError(f"Input file {input_path} not found.")

    # 1) load full-res
    orig = cv2.imread(input_path)
    oh, ow = orig.shape[:2]

    # 2) small copy for detection
    scale = min(max(WIDTH, HEIGHT) / float(max(ow, oh)), 1.0)
    small = cv2.resize(orig,
                       (int(ow * scale), int(oh * scale)),
                       interpolation=cv2.INTER_AREA)

    # 3) detect & rescale contour
    doc_cnt_small = scan_detection(small)
    doc_cnt = (doc_cnt_small / scale).astype("float32")

    # 4) warp full-res
    warped = four_point_transform(orig, doc_cnt)

    # Returns scan
    if output_type == 'scan':
        proc = image_processing(warped)
        proc = proc[10:proc.shape[0]-10, 10:proc.shape[1]-10] # Removes document edge

        # encode to JPEG in memory
        success, buf = cv2.imencode('.jpg', proc)
        if not success:
            raise RuntimeError("Could not encode image to JPEG")
        return buf.tobytes()

    # Returns text
    elif output_type == 'text':
        text = pytesseract.image_to_string(warped).strip()
        return text

    # Invalid output type
    else:
        raise ValueError("output_type must be 'scan' or 'text'.")
