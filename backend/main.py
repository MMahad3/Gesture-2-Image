from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import base64
import io
from PIL import Image
import os
import uuid
import torch
from diffusers import StableDiffusionPipeline
from typing import Optional

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create folder for generated images if it doesn't exist
GENERATED_DIR = "generated_images"
os.makedirs(GENERATED_DIR, exist_ok=True)

# Mount static files so images can be accessed via URL
app.mount("/images", StaticFiles(directory=GENERATED_DIR), name="images")

# Feature toggle
FEATURE2 = os.getenv("FEATURE2_ENABLED", "true").lower() == "true"

# Lazy model loading
pipe = None

def load_model():
    global pipe
    if pipe is None:
        print("Loading Stable Diffusion model...")
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float32  # Use float32 for CPU
        )
        pipe = pipe.to("cpu")
        print("Model loaded successfully")

class GenerateStreamQuery(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None        

class PromptRequest(BaseModel):
    prompt: str
    negative_prompt: str = None

@app.post("/api/recognize")
async def recognize_gesture(request: Request):
    try:
        data = await request.json()
        gesture = data.get('gesture')
        
        if not gesture:
            raise HTTPException(status_code=400, detail="Gesture data is required")
            
        return {
            "message": f"Gesture '{gesture}' recognized successfully",
            "gesture": gesture,
            "confidence": 0.855
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_image(prompt_req: PromptRequest):
    if not FEATURE2:
        raise HTTPException(
            status_code=403,
            detail="Image generation feature is not enabled. Set FEATURE2_ENABLED=true to enable."
        )

    try:
        load_model()

        generator = torch.Generator(device="cpu").manual_seed(42)
        num_steps = 15

        pipe.scheduler = pipe.scheduler.from_config(pipe.scheduler.config)
        pipe.scheduler.set_timesteps(num_inference_steps=num_steps)

        image = pipe(
            prompt_req.prompt,
            negative_prompt=prompt_req.negative_prompt,
            generator=generator,
            num_inference_steps=num_steps
        ).images[0]

        # Save image to file
        filename = f"{uuid.uuid4().hex}.png"
        file_path = os.path.join(GENERATED_DIR, filename)
        image.save(file_path)

        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return {
            "status": "success",
            "prompt": prompt_req.prompt,
            "image": f"data:image/png;base64,{img_str}",
            "image_url": f"/images/{filename}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {str(e)}"
        )

@app.get("/api/generate-stream")
async def generate_image_stream(
    prompt: str = Query(..., description="The prompt for image generation"),
    negative_prompt: str = Query(None, description="Negative prompt for image generation")
):
    if not FEATURE2:
        raise HTTPException(
            status_code=403,
            detail="Image generation feature is not enabled."
        )

    async def event_stream():
        try:
            yield f"event: status\ndata: Loading Stable Diffusion model...\n\n"
            load_model()
            yield f"event: status\ndata: Model loaded successfully\n\n"

            generator = torch.Generator(device="cpu").manual_seed(42)
            num_steps = 15
            pipe.scheduler = pipe.scheduler.from_config(pipe.scheduler.config)
            pipe.scheduler.set_timesteps(num_inference_steps=num_steps)

            yield f"event: status\ndata: Starting image generation...\n\n"

            for i, timestep in enumerate(pipe.scheduler.timesteps[:num_steps]):
                progress = (i + 1) / num_steps * 100
                yield f"event: progress\ndata: {int(progress)}% complete\n\n"
                await asyncio.sleep(0.1)

            image = pipe(
                prompt,
                negative_prompt=negative_prompt,
                generator=generator,
                num_inference_steps=num_steps
            ).images[0]

            filename = f"{uuid.uuid4().hex}.png"
            file_path = os.path.join(GENERATED_DIR, filename)
            image.save(file_path)

            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            yield f"event: complete\ndata: Image generation complete!\n\n"
            yield f"event: image\ndata: data:image/png;base64,{img_str}\n\n"
            yield f"event: image_url\ndata: /images/{filename}\n\n"

        except Exception as e:
            yield f"event: error\ndata: Error: {str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/favicon.ico")
async def favicon():
    return {"message": "ok"}
