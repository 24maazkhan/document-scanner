import requests
import os
import argparse

SERVER_URL = 'http://localhost:5000'


def test_scan(input_path, output_path):
    with open(input_path, 'rb') as img_file:
        files = {'file': img_file}
        resp = requests.post(f'{SERVER_URL}/scan', files=files)

    if resp.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(resp.content)
        print(f'Scan saved to {output_path}')
    else:
        print(f'Scan request failed [{resp.status_code}]: {resp.text}')


def test_ocr(input_path, output_path):
    with open(input_path, 'rb') as img_file:
        files = {'file': img_file}
        resp = requests.post(f'{SERVER_URL}/ocr', files=files)

    if resp.status_code == 200:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print(f'OCR text saved to {output_path}')
    else:
        print(f'OCR request failed [{resp.status_code}]: {resp.text}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test scanner Flask API')
    parser.add_argument('mode', choices=['scan', 'ocr', 'all'],
                        help='Which endpoint to test')
    parser.add_argument('--input', '-i', default='input.jpg',
                        help='Path to input image file')
    parser.add_argument('--out', '-o', default='test_output',
                        help='Directory to store outputs')
    args = parser.parse_args()

    # ensure output directory exists
    os.makedirs(args.out, exist_ok=True)

    base = os.path.splitext(os.path.basename(args.input))[0]
    if args.mode in ('scan', 'all'):
        scan_out = os.path.join(args.out, f"{base}_scanned.jpg")
        test_scan(args.input, scan_out)

    if args.mode in ('ocr', 'all'):
        ocr_out = os.path.join(args.out, f"{base}_recognized.txt")
        test_ocr(args.input, ocr_out)
