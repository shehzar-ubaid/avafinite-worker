import runpod
import requests
import json
import base64
import time
import os

def wait_for_comfyui():
    # Barha kar 5 minute (300 seconds) kar diya hai kyunki SeedVR2/Models load hone mein time lete hain
    for _ in range(150): 
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
    start_time = time.time() # Global safety timer start
    
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

    # Logic 1: Audio + Lip-sync (Node 15)
    if "15" in workflow:
        workflow["15"]["inputs"]["text"] = prompt
        workflow["15"]["inputs"]["voice"] = voice_id

    # Logic 2: Action/Motion from prompt (Node 6)
    if "6" in workflow:
        workflow["6"]["inputs"]["text"] = prompt

    # Logic 3: Custom Captions (Node 10)
    if "10" in workflow:
        workflow["10"]["inputs"]["text"] = user_captions

    # Logic 4: Video Enhancement (SeedVR2 - Node 30)
    if "30" in workflow:
        workflow["30"]["inputs"]["upscale_by"] = upscale_factor

    # Send to ComfyUI
    response = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow}).json()
    prompt_id = response['prompt_id']

    # Wait for final MP4 with Safety Timeout
    while True:
        # Agar processing 15 minute se upar chali jaye to error return karein
        if time.time() - start_time > 900: 
            return {"status": "error", "message": "Job processing timeout (15 mins limit)"}

        history_res = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}").json()
        if prompt_id in history_res:
            outputs = history_res[prompt_id]['outputs']
            for node_id, node_output in outputs.items():
                if 'gifs' in node_output or 'videos' in node_output:
                    key = 'gifs' if 'gifs' in node_output else 'videos'
                    video_file = node_output[key]['filename']
                    filepath = f"output/{video_file}"
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as f:
                            return {
                                "status": "success",
                                "video_base64": base64.b64encode(f.read()).decode('utf-8'),
                                "filename": video_file
                            }
        time.sleep(5) # Thora zyada gap taaki API spam na ho

runpod.serverless.start({"handler": handler})