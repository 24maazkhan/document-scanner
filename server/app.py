from flask import Flask, request, send_file, abort
from io import BytesIO
from werkzeug.utils import secure_filename
import os
from scan_function import process_file
import tempfile

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan_endpoint():
    # Verify data present
    if 'file' not in request.files:
        abort(400, "No file part")
    upload = request.files['file']
    if upload.filename == '':
        abort(400, "No selected file")

    # Temporarily save the uploaded file
    filename = secure_filename(upload.filename)
    tmp_dir  = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, filename)
    upload.save(tmp_path)

    # process and get JPEG bytes
    img_bytes = process_file(tmp_path, output_type='scan')
    out_name = f"{os.path.splitext(filename)[0]}_scanned.jpg"

    # Send JPEG File
    return send_file(
        BytesIO(img_bytes),
        mimetype='image/jpeg',
        as_attachment=True,
        download_name=out_name
    )

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    # Verify data present
    if 'file' not in request.files:
        abort(400, "No file part")
    upload = request.files['file']
    if upload.filename == '':
        abort(400, "No selected file")

    # Temporarily save the uploaded file
    filename = secure_filename(upload.filename)
    tmp_dir  = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, filename)
    upload.save(tmp_path)

    # process and get string
    text = process_file(tmp_path, output_type='text')
    out_name = f"{os.path.splitext(filename)[0]}_recognized.txt"

    # Send text file
    return send_file(
        BytesIO(text.encode('utf-8')),
        mimetype='text/plain',
        as_attachment=True,
        download_name=out_name
    )

if __name__ == '__main__':
    app.run(port=5000, debug=True)
