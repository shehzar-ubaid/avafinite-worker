FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git python3-pip python3-dev ffmpeg libgl1-mesa-glx libglib2.0-0 wget

WORKDIR /app
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install runpod # RunPod worker ke liye zaroori

# Subtitles ke liye zaroori nodes
WORKDIR /app/custom_nodes
RUN git clone https://github.com/AlekPet/ComfyUI_Custom_Nodes_AlekPet.git
RUN git clone https://github.com/jovandant/ComfyUI-VideoHelperSuite.git

WORKDIR /app
COPY handler.py .
COPY workflow_api.json . 

# Pehle ComfyUI start hoga, phir worker
CMD python3 main.py --listen 0.0.0.0 & python3 -u handler.py