#Using ngrok to connect flask backend to the react frontend
from pyngrok import ngrok
public_url = ngrok.connect(5000).public_url
print("Public API URL:", public_url)

#flask server
from flask import Flask, request, jsonify
import os
import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from PIL import Image
from flask_cors import CORS
import cv2
import numpy as np
import base64
from io import BytesIO
import http.client
import json
import time
import requests
import shutil

app = Flask(__name__)
CORS(app,origins=["http://localhost:3000"])  # Allow React frontend

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'results'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

API_KEY = "d662df79ecf6a2ed3ea91b679cd04decde39496bdaf864a58199c39419e811bb"

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# STEP 1: Process sketch image (Canny edge detection)
def load_sketch(path):
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (512, 512))
    edges = cv2.Canny(image, 100, 200)
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(edges_rgb)

# STEP 2: Load models and generate image
def generate_realistic_image(sketch_path, prompt, output_path="result.png"):
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/sd-controlnet-canny", torch_dtype=torch.float16
    )

    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        controlnet=controlnet,
        safety_checker=None,
        torch_dtype=torch.float16,
    ).to("cuda")

    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    sketch_image = load_sketch(sketch_path)

    image = pipe(
        prompt,
        num_inference_steps=30,
        image=sketch_image,
        generator=torch.manual_seed(42)
    ).images[0]

    image.save(output_path)
    print(f"Saved to {output_path}")
    return output_path

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def send_to_piapi(base64_image):
    conn = http.client.HTTPSConnection("api.piapi.ai")
    payload = json.dumps({
        "model": "Qubico/trellis",
        "task_type": "image-to-3d",
        "input": {
            "image": base64_image,
            "seed": 0,
            "ss_sampling_steps": 75,
            "slat_sampling_steps": 75,
            "ss_guidance_strength": 7.5,
            "slat_guidance_strength": 7
        },
        "config": {
            "webhook_config": {
                "endpoint": "string",
                "secret": "string"
            }
        }
    })
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/api/v1/task", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    task_id = data["data"]["task_id"]
    print(task_id)

    # Poll for result
    while(True):
        time.sleep(5)
        response = requests.get(f"https://api.piapi.ai/api/v1/task/{task_id}", headers=headers)
        result = response.json()
        status = result["data"]["status"].lower()
        print(status)
        if status == "completed":
            return result["data"]["output"]["model_file"]
        elif status == "failed":
            return None
    return None

# STEP 3: Flask endpoint to receive requests
@app.route('/upload', methods=['POST'])
def handle_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    prompt = request.form.get("prompt", "Analyze and generate a clean, flat 2D color illustration. Identify the pose and individual elements such as body parts, objects, or clothing. Assign appropriate, realistic colors to each component (e.g., skin tone, hair, clothing, objects), while preserving the proportions and structure. The background must be plain white. Avoid adding shadows, lighting effects, gradients, or depth. Focus on clean outlines, solid fill colors, and a flat, illustrative art style similar to digital cartoons or 2D vector drawings.")

    try:
        # Save uploaded image
        sketch_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(sketch_path)

        # Generate 2D image
        output_path = generate_realistic_image(sketch_path, prompt)

        base64_image = encode_image_to_base64(output_path)
        filename = os.path.basename(output_path)

        return jsonify({
            'message': 'Success',
            'image_base64': base64_image,
            'filename': filename
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send-local-image', methods=['POST'])
def send_local_image():
    data = request.json
    filename = data.get('filename')

    if not filename:
        return jsonify({'error': 'Missing filename'}), 400

    model_url = send_to_piapi(filename)
    if not model_url:
        return jsonify({'error': '3D model generation failed'}), 500

    return jsonify({
        'model_url': model_url,
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
