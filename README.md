# Gesture-to-Image Generation using Deep Learning and Generative AI 

This project explores the fusion of **computer vision** and **generative AI** by translating **hand gestures into images** using **MediaPipe Hands** and **Stable Diffusion**.

## 📌 Objective

To develop a system capable of detecting hand gestures in real-time and generating a contextually relevant image using generative AI, enabling intuitive visual creativity through human gestures.

## 🧩 Problem Statement

While text-to-image generation is widely researched, **gesture-based control for image generation** is still underexplored. This project addresses the challenge of bridging this gap by building a system that transforms hand gestures into visual outputs using state-of-the-art models.

## ⚙️ Methodology

- **Hand Gesture Detection**: 
  - Implemented using **MediaPipe Hands** by Google, which tracks 21 3D landmarks per hand using a lightweight CNN+BlazePose architecture.

- **Gesture Mapping**: 
  - Predefined gestures are mapped to corresponding image prompts (e.g., a “peace” sign maps to the prompt "sunset on a beach").

- **Image Generation**: 
  - Leveraged **Stable Diffusion**, a latent diffusion model (LDM), to generate photorealistic images based on the prompt.
  - The image is generated through 15 **denoising steps**, where random noise is progressively refined into an image using a U-Net guided by a CLIP-based text encoder.

## 🖼️ Results

- Successfully detected multiple hand gestures in real-time using webcam input.
- Generated visually accurate and contextually aligned images based on gesture-mapped prompts.
- Demonstrated practical application of gesture-controlled generative systems.

## 📚 References

- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands)
- [Stable Diffusion (CompVis)](https://github.com/CompVis/stable-diffusion)
- [Diffusers Library by HuggingFace](https://github.com/huggingface/diffusers)
- [Gesture Recognition with OpenCV + MediaPipe](https://google.github.io/mediapipe/)

---

## 🧪 Future Improvements

- Dynamic prompt generation using gesture context.
- Training custom gestures and fine-tuned diffusion models.
- Integration with AR/VR for immersive gesture-controlled creativity.

---

## 🚀 How to Run

```bash
git clone https://github.com/yourusername/Gesture-2-Image
cd Gesture-2-Image

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
npm install

# Run the Backend
python main.py

#Run the Frontend
npm start
