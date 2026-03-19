import runpod
import requests
import json
import os
import time

def wait_for_comfyui():
    print("Waiting for ComfyUI to start...")
    while True:
        try:
            response = requests.get("http://127.0.0.1:8188/history")
            if response.status_code == 200:
                break
        except:
            time.sleep(2)

def handler(job):
    wait_for_comfyui()
    job_input = job['input']
    
    # User Inputs from Frontend
    prompt_text = job_input.get("prompt", "")
    voice_ref = job_input.get("reference_voice", "default")
    quality = job_input.get("quality", "720p") # Default quality

    # Mapping Quality to Upscale Factor
    # SeedVR2 ya general upscalers factor (2x, 4x) par kaam karte hain
    quality_map = {
        "480p": 1,
        "720p": 1.5,
        "1080p": 2,
        "4k": 4,
        "8k": 8
    }
    upscale_factor = quality_map.get(quality.lower(), 1.5)

    # 1. Load Workflow API JSON
    with open("workflow_api.json", "r") as f:
        workflow = json.load(f)

    # 2. Logic: ChatterboxTTS (Audio)
    # Yahan hum reference voice aur text ko map karenge
    if "15" in workflow: # Farz karein Node 15 Audio Input hai
        workflow["15"]["inputs"]["text"] = prompt_text
        workflow["15"]["inputs"]["voice"] = voice_ref

    # 3. Logic: HuMo (Motion)
    if "6" in workflow: # Motion Prompt Node
        workflow["6"]["inputs"]["text"] = prompt_text

    # 4. Logic: SeedVR2 (Quality Enhancer)
    # Node ID 30 aapka SeedVR2 Upscaler node hona chahiye
    if "30" in workflow:
        workflow["30"]["inputs"]["upscale_by"] = upscale_factor
        print(f"Enhancing video to {quality} (Factor: {upscale_factor}x)")

    # 5. Send to ComfyUI
    try:
        response = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow})
        return {
            "status": "success",
            "job_id": job['id'],
            "target_quality": quality,
            "message": "Processing Audio, Motion, and Upscaling..."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

runpod.serverless.start({"handler": handler})