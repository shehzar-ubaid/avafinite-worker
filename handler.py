import runpod
import requests
import json
import base64
import time
import os

def wait_for_comfyui():
    while True:
        try:
            response = requests.get("http://127.0.0.1:8188/history")
            if response.status_code == 200: break
        except: time.sleep(2)

def handler(job):
    wait_for_comfyui()
    job_input = job['input']
    
    # User Requirements
    prompt = job_input.get("prompt", "")
    voice_id = job_input.get("voiceId", "default")
    user_captions = job_input.get("subtitle", "") # Captions feature
    quality = job_input.get("quality", "720p") # Enhancement feature

    # Quality Mapping for SeedVR2
    quality_map = {"480p": 1, "720p": 1.5, "1080p": 2, "4k": 4}
    upscale_factor = quality_map.get(quality.lower(), 1.5)

    with open("workflow_api.json", "r") as f:
        workflow = json.load(f)

    # Logic 1: Audio & Lip-sync
    if "15" in workflow:
        workflow["15"]["inputs"]["text"] = prompt
        workflow["15"]["inputs"]["voice"] = voice_id

    # Logic 2: Action/Motion
    if "6" in workflow:
        workflow["6"]["inputs"]["text"] = prompt

    # Logic 3: Custom Captions
    if "10" in workflow:
        workflow["10"]["inputs"]["text"] = user_captions

    # Logic 4: Video Enhancement (SeedVR2)
    if "30" in workflow:
        workflow["30"]["inputs"]["upscale_by"] = upscale_factor

    # ComfyUI ko prompt bhejna
    response = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow}).json()
    prompt_id = response['prompt_id']

    # Final MP4 Output wait logic
    while True:
        history = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}").json()
        if prompt_id in history:
            outputs = history[prompt_id]['outputs']
            for node_id in outputs:
                if 'gifs' in outputs[node_id]: # VideoCombine node
                    video_file = outputs[node_id]['gifs']['filename']
                    with open(f"output/{video_file}", "rb") as f:
                        return {"video_base64": base64.b64encode(f.read()).decode('utf-8')}
        time.sleep(2)

runpod.serverless.start({"handler": handler})