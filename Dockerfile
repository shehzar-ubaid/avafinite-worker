FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git python3-pip python3-dev ffmpeg libgl1-mesa-glx libglib2.0-0 wget

WORKDIR /app
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .
RUN pip3 install --no-cache-dir -r requirements.txt || true
RUN pip3 install --no-cache-dir runpod requests

WORKDIR /app/custom_nodes
RUN git clone https://github.com/AlekPet/ComfyUI_Custom_Nodes_AlekPet.git || true
RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git || true
RUN git clone https://github.com/jovandant/ComfyUI-VideoHelperSuite.git || true
# SeedVR2 Upscaler Node add kiya gaya hai
RUN git clone https://github.com/AIGODLIKE/ComfyUI-SeedVR2.git || true

WORKDIR /app
COPY handler.py .
COPY workflow_api.json* ./

EXPOSE 8188    

CMD ["sh", "-c", "python3 main.py --listen 0.0.0.0 & python3 -u handler.py"]