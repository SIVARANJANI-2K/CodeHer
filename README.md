# Sketch2Reality: From Simple Sketch to 2D & 3D Magic

> Generate realistic 2D and 3D models from hand-drawn sketches using AI!

---

## Demo Video

 [Watch the Demo](https://github.com/user-attachments/assets/679fa2fc-e248-4d22-b29f-ff1203a4ae00)

---

## Tech Stack

| Layer         | Technology       |
|---------------|------------------|
|  Frontend   | React            |
| Backend    | Flask            |
| AI Models  | Stable Diffusion, ControlNet |
| APIs       | PiAPI, Gemini API |

---

##  How It Works

1. **Sketch Upload**  
   - User uploads a hand-drawn sketch via the React frontend.

2. **2D Model Generation**  
   - The sketch is sent to the Flask backend.
   - ControlNet + Stable Diffusion (from RunwayML) is used to enhance and generate a detailed 2D model.

3. **3D Model Generation**  
   - The generated 2D image is passed to **PiAPI**, which returns a fully-formed 3D model.

4. **Context & Descriptions**  
   - The Gemini API is optionally used to generate a textual description of the model or assist with understanding the sketch.

---
## 🧰 Requirements

### Backend
- Python 3.8+
- Flask
- `diffusers`, `transformers`, `torch`, `PIL`, `requests`, `flask-cors`, etc.

### Frontend
- React (with Axios or Fetch)
- File upload component

---

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/sketch2model.git
cd sketch2model
