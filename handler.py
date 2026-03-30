import runpod
import requests
import json
import base64
import time
import os 

COMFYUI_OUTPUT_PATH = "/app/output"
  
def wait_for_comfyui():
    for _ in range(150):    
        try:
            response = requests.get("http://127.0.0.1:8188/history")
            if response.status_code == 200:
                return
        except:
            pass
        time.sleep(2)
    raise Exception("FATAL: ComfyUI failed to start within 5 minutes. Check GPU VRAM or Model paths.")

def handler(job):
    try:
        wait_for_comfyui()
        job_input = job['input']
        start_time = time.time()
        
        # User Inputs
        prompt = job_input.get("prompt", "A person speaking naturally")
        voice_id = job_input.get("voiceId", "default")
        user_captions = job_input.get("subtitle", "")
        quality = job_input.get("quality", "720p")

        with open("workflow_api.json", "r") as f:
            workflow = json.load(f)

        # Node Updates (sab requirements cover ho rahe hain)
        if "15" in workflow: 
            workflow["15"]["inputs"]["text"] = prompt
            workflow["15"]["inputs"]["voice"] = voice_id
        if "6" in workflow: 
            workflow["6"]["inputs"]["text"] = prompt
        if "10" in workflow: 
            workflow["10"]["inputs"]["text"] = user_captions
        if "30" in workflow: 
            # Quality enhancement (SeedVR2)
            quality_map = {"480p": 1, "720p": 1.5, "1080p": 2, "4k": 4}
            upscale_factor = quality_map.get(quality.lower(), 1.5)
            workflow["30"]["inputs"]["upscale_by"] = upscale_factor

        # Send prompt
        res = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow})
        if res.status_code != 200:
            return {"status": "error", "message": f"ComfyUI API Rejected: {res.text}"}
        
        prompt_id = res.json()['prompt_id']

        while True:
            if time.time() - start_time > 1200:
                return {"status": "error", "message": "Global Timeout: Video generation took > 20 mins"}

            history_res = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}").json()
            
            if prompt_id in history_res:
                outputs = history_res[prompt_id]['outputs']
                for node_id, node_output in outputs.items():
                    file_info = None
                    if 'videos' in node_output:
                        file_info = node_output['videos']
                    elif 'gifs' in node_output:
                        file_info = node_output['gifs']

                    if file_info and isinstance(file_info, list) and len(file_info) > 0:
                        video_file = file_info[0]['filename']   # ← Yeh fix hai
                        filepath = os.path.join(COMFYUI_OUTPUT_PATH, video_file)
                        
                        if os.path.exists(filepath):
                            with open(filepath, "rb") as f:
                                return {
                                    "status": "success",
                                    "video_base64": base64.b64encode(f.read()).decode('utf-8'),
                                    "filename": video_file
                                }
            time.sleep(5)
            
    except Exception as e:
        return {"status": "error", "message": f"Runtime Error: {str(e)}"}

runpod.serverless.start({"handler": handler})