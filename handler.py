import runpod
import requests
import json
import time
import os

def wait_for_comfyui():
    print("Waiting for ComfyUI to start...")
    while True:
        try:
            response = requests.get("http://127.0.0.1:8188/history")
            if response.status_code == 200:
                print("ComfyUI is UP!")
                break
        except:
            time.sleep(2)

def handler(job):
    wait_for_comfyui()
    job_input = job['input']
    
    prompt_text = job_input.get("prompt", "A realistic video")
    subtitle_text = job_input.get("subtitle_text", "")
    upscale_val = job_input.get("upscale_factor", 2) # Default 2x upscale

    file_path = "workflow_api.json"
    if not os.path.exists(file_path):
        return {"error": "workflow_api.json not found inside container."}

    with open(file_path, "r") as f:
        workflow = json.load(f)

    # Prompt Update [cite: 34]
    if "6" in workflow:
        workflow["6"]["inputs"]["text"] = prompt_text
    
    # Subtitle Update [cite: 34]
    if subtitle_text and "10" in workflow:
        workflow["10"]["inputs"]["text"] = subtitle_text
        workflow["10"]["inputs"]["color"] = job_input.get("font_color", "white")

    # SeedVR2 Upscale Update (فرض karein upscale node ID 30 hai)
    if "30" in workflow:
        workflow["30"]["inputs"]["upscale_by"] = upscale_val

    payload = {"prompt": workflow}
    try:
        response = requests.post("http://127.0.0.1:8188/prompt", json=payload)
        return {"status": "success", "response": response.json(), "upscale": f"{upscale_val}x applied"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

runpod.serverless.start({"handler": handler})