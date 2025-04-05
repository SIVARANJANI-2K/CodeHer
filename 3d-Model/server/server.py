from flask import Flask, jsonify
from flask_cors import CORS
import os
import shutil
import base64
import http.client
import json
import time
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

API_KEY = "9831af8f6426e3b414d8218ef43322ee9fd3de514cad71ef1becc567fb29f9fa"  # Your real key
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

@app.route('/send-local-image', methods=['POST'])
def send_local_image():
    try:
        # Original image path
        image_path = "C:\\Users\\Sivakumar\\Downloads\\Untitled.png"
        
        # Destination directory
        save_dir = "saved_images"
        os.makedirs(save_dir, exist_ok=True)  # Create directory if it doesn't exist
        
        # Destination file path
        destination_path = os.path.join(save_dir, "Untitled.png")
        print(destination_path)
        # Copy image to destination
        shutil.copy(image_path, destination_path)
        image_base64 = encode_image_to_base64(destination_path)


        conn = http.client.HTTPSConnection("api.piapi.ai")
        payload = json.dumps({
            "model": "Qubico/trellis",
                "task_type": "image-to-3d",
            "input": {
                "image": image_base64,
                "seed": 0,
                "ss_sampling_steps": 50,
                "slat_sampling_steps": 50,
                "ss_guidance_strength": 7.5,
                "slat_guidance_strength": 3
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
        # Polling for status
        while True:  # Poll 20 times max
            time.sleep(5)
            response = requests.get(f"https://api.piapi.ai/api/v1/task/{task_id}", headers={"x-api-key": API_KEY})
            result = response.json()
            status = result["data"]["status"].lower()
            print(status)
            if status == "completed":
                model_url = result["data"]["output"]["model_file"]
                print(model_url)
                return jsonify({"modelUrl": model_url}), 200
            elif status == "failed":
                return jsonify({"error": "Model generation failed"}), 500

        return jsonify({"error": "Model generation timed out"}), 504
        print(f"Image copied to {destination_path}")
        return jsonify({'message': 'Image saved successfully!'}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
