import runpod
import requests
import json
import base64
import time

def wait_for_comfyui():
    while True:
        try:
            response = requests.get("http://127.0.0.1:8188/history")
            if response.status_code == 200: break
        except: time.sleep(2)

def handler(job):
    wait_for_comfyui()
    job_input = job['input']
    
    # User Inputs
    prompt_text = job_input.get("prompt", "")
    voice_ref = job_input.get("voiceId", "default")
    quality = job_input.get("quality", "720p")
    user_captions = job_input.get("subtitle", "") # Frontend se captions

    # Quality Mapping
    quality_map = {"480p": 1, "720p": 1.5, "1080p": 2, "4k": 4, "8k": 8}
    upscale_factor = quality_map.get(quality.lower(), 1.5)

    with open("workflow_api.json", "r") as f:
        workflow = json.load(f)

    # 1. Lip-sync & Action Mapping
    if "6" in workflow: workflow["6"]["inputs"]["text"] = prompt_text
    
    # 2. Audio Generation (Chatterbox)
    if "15" in workflow:
        workflow["15"]["inputs"]["text"] = prompt_text
        workflow["15"]["inputs"]["voice"] = voice_ref

    # 3. Dynamic Captions Fix
    if "10" in workflow:
        workflow["10"]["inputs"]["text"] = user_captions
        print(f"Applying Captions: {user_captions}")

    # 4. SeedVR2 Quality Enhancement
    if "30" in workflow:
        workflow["30"]["inputs"]["upscale_by"] = upscale_factor

    # Push to ComfyUI
    prompt = {"prompt": workflow}
    response = requests.post("http://127.0.0.1:8188/prompt", json=prompt).json()
    prompt_id = response['prompt_id']

    # Wait for MP4 Output
    while True:
        history = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}").json()
        if prompt_id in history:
            # Video path extraction
            outputs = history[prompt_id]['outputs']
            for node_id in outputs:
                if 'gifs' in outputs[node_id]:
                    video_data = outputs[node_id]['gifs']['filename']
                    # File ko base64 mein convert karke bhejein
                    with open(f"output/{video_data}", "rb") as v_file:
                        encoded_video = base64.b64encode(v_file.read()).decode('utf-8')
                    return {"video_base64": encoded_video}
        time.sleep(2)

runpod.serverless.start({"handler": handler})