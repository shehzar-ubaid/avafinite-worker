import runpod
import requests
import json
import time
import os

# ComfyUI ko backend mein start karne ka wait
def wait_for_comfyui():
    while True:
        try:
            requests.get("http://127.0.0.1:8188")
            break
        except:
            time.sleep(1)

def handler(job):
    job_input = job['input']
    
    # User se input lena (Subtitles details)
    prompt_text = job_input.get("prompt", "A realistic video")
    subtitle_text = job_input.get("subtitle_text", "")
    font_color = job_input.get("font_color", "white")
    font_size = job_input.get("font_size", 40)
    animation_style = job_input.get("animation", "fade") # e.g., fade, slide, pop

    # Yahan aap apna ComfyUI Workflow JSON load karenge
    # Hum workflow mein subtitle nodes ko user ke input se replace karenge
    with open("workflow_api.json", "r") as f:
        workflow = json.load(f)

    # Workflow update logic (Yahan nodes ki ID aapke workflow ke mutabiq hogi)
    workflow["6"]["inputs"]["text"] = prompt_text # Positive Prompt
    if subtitle_text:
        # फर्ज karein node ID 10 aapka subtitle node hai
        workflow["10"]["inputs"]["text"] = subtitle_text
        workflow["10"]["inputs"]["color"] = font_color
        workflow["10"]["inputs"]["animation"] = animation_style

    # ComfyUI ko request bhejna
    payload = {"prompt": workflow}
    response = requests.post("http://127.0.0.1:8188/prompt", json=payload)
    
    # Output file dhoond kar return karna (simplification)
    # Asal mein yahan S3 bucket ya link return hota hai
    return {"message": "Video generated successfully", "status": "completed"}

runpod.serverless.start({"handler": handler})