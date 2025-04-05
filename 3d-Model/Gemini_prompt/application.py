from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import google.generativeai as genai
from werkzeug.utils import secure_filename # Update this line

app = Flask(__name__)
CORS(app)

# Configure your Gemini API key
genai.configure(api_key="AIzaSyAbkhcGkTunotds5crYdxNpkOIj_32nSrg")  # Replace this

# File upload configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate-prompt", methods=["POST"])
def generate_prompt():
    print("Received generate-prompt request")
    if 'image' not in request.files:
        print("Error: No image uploaded")
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        print("Error: Empty filename")
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(image_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f"Saving file to: {filepath}")
    image_file.save(filepath)
    print(f"File saved successfully")

    try:
        with open(filepath, "rb") as img:
            image_data = img.read()
            print(f"Image data read successfully. Size: {len(image_data)} bytes")

        prompt_text = "Describe this pencil sketch into a highly detailed, realistic 2D illustration. Focus on enhancing the depth, texture, and lighting to bring the sketch to life. Add realistic shading, colors, and proportions, ensuring all elements are accurately represented. Pay attention to material details such as the texture of surfaces (wood, metal, fabric, etc.) and the play of light and shadow. Create a composition that captures a lifelike quality, with lifelike dimensions, and depth while maintaining the integrity of the original sketch accurately with 75 words"

        print("Calling Gemini API...")
        response = model.generate_content([
            prompt_text,
            {
                "mime_type": "image/png",
                "data": image_data
            }
        ])
        print("Gemini API call successful")

        description = response.text.strip()
        print(f"Generated description: {description}")
        return jsonify({'description': description})

    except Exception as e:
        print("Error during Gemini API call or processing:", str(e))
        return jsonify({'error': 'Failed to generate description'}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)
