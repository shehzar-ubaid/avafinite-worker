import runpod
import requests
import json
import base64
import time
import os

def wait_for_comfyui():
    for _ in range(60):  # max 2 minute wait
        try:
            response = requests.get("http://127.0.0.1:8188/history")
            if response.status_code == 200:
                print("✅ ComfyUI ready!")
                return
        except:
            pass
        time.sleep(2)
    raise Exception("ComfyUI not ready in time")

def handler(job):
    wait_for_comfyui()
    job_input = job['input']
    
    # User Inputs
    prompt = job_input.get("prompt", "A person speaking naturally")
    voice_id = job_input.get("voiceId", "default")
    user_captions = job_input.get("subtitle", "")
    quality = job_input.get("quality", "720p")

    # Quality Mapping for SeedVR2
    quality_map = {"480p": 1, "720p": 1.5, "1080p": 2, "4k": 4}
    upscale_factor = quality_map.get(quality.lower(), 1.5)

    with open("workflow_api.json", "r") as f:
        workflow = json.load(f)

    # Logic 1: Audio + Lip-sync
    if "15" in workflow:
        workflow["15"]["inputs"]["text"] = prompt
        workflow["15"]["inputs"]["voice"] = voice_id

    # Logic 2: Action/Motion from prompt
    if "6" in workflow:
        workflow["6"]["inputs"]["text"] = prompt

    # Logic 3: Custom Captions
    if "10" in workflow:
        workflow["10"]["inputs"]["text"] = user_captions

    # Logic 4: Video Enhancement (SeedVR2)
    if "30" in workflow:
        workflow["30"]["inputs"]["upscale_by"] = upscale_factor

    # Send to ComfyUI
    response = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow}).json()
    prompt_id = response['prompt_id']

    # Wait for final MP4
    while True:
        history = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}").json()
        if prompt_id in history:
            outputs = history[prompt_id]['outputs']
            for node_id, node_output in outputs.items():
                if 'gifs' in node_output or 'videos' in node_output:
                    key = 'gifs' if 'gifs' in node_output else 'videos'
                    video_file = node_output[key][0]['filename']
                    filepath = f"output/{video_file}"
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as f:
                            return {
                                "status": "success",
                                "video_base64": base64.b64encode(f.read()).decode('utf-8'),
                                "filename": video_file
                            }
        time.sleep(2)

runpod.serverless.start({"handler": handler})