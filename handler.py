import runpod
import requests
import json
import time
import os

# ComfyUI ko backend mein start karne ka wait (Fix: Isay ab call kiya jayega)
def wait_for_comfyui():
    print("Waiting for ComfyUI to start...")
    while True:
        try:
            response = requests.get("http://127.0.0.1:8188/history")
            if response.status_code == 200:
                print("ComfyUI is UP and running!")
                break
        except:
            time.sleep(2)

def handler(job):
    # Sabse pehle wait karein taake ComfyUI load ho jaye
    wait_for_comfyui()
    
    job_input = job['input']
    
    # User Inputs
    prompt_text = job_input.get("prompt", "A realistic video")
    subtitle_text = job_input.get("subtitle_text", "")
    font_color = job_input.get("font_color", "white")
    font_size = job_input.get("font_size", 40)
    animation_style = job_input.get("animation", "fade")

    # File load karne ka paka tareeqa
    file_path = os.path.join(os.getcwd(), "workflow_api.json")
    if not os.path.exists(file_path):
        return {"error": f"workflow_api.json not found at {file_path}. Please ensure it is in your repo."}

    with open(file_path, "r") as f:
        workflow = json.load(f)

    # Workflow Update Logic
    # Note: Apne Workflow JSON mein Node IDs lazmi check karein
    try:
        if "6" in workflow:
            workflow["6"]["inputs"]["text"] = prompt_text
        
        if subtitle_text and "10" in workflow:
            workflow["10"]["inputs"]["text"] = subtitle_text
            workflow["10"]["inputs"]["color"] = font_color
            workflow["10"]["inputs"]["font_size"] = font_size
            workflow["10"]["inputs"]["animation"] = animation_style
    except KeyError as e:
        print(f"Warning: Node ID {e} not found in JSON. Check your workflow IDs.")

    # Request to ComfyUI
    payload = {"prompt": workflow}
    try:
        response = requests.post("http://127.0.0.1:8188/prompt", json=payload)
        return {"status": "success", "response": response.json(), "message": "Video task sent to ComfyUI"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

runpod.serverless.start({"handler": handler})