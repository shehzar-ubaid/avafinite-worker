FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git python3-pip ffmpeg libgl1-mesa-glx libglib2.0-0 wget

WORKDIR /app
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir runpod requests

WORKDIR /app/custom_nodes
# Captions aur Video Merge ke liye nodes
RUN git clone https://github.com/pythongosssss/ComfyUI-Custom-Nodes.git || true
RUN git clone https://github.com/jovandant/ComfyUI-VideoHelperSuite.git || true
# Video Quality Enhancement
RUN git clone https://github.com/AIGODLIKE/ComfyUI-SeedVR2.git || true

WORKDIR /app
COPY handler.py .
COPY workflow_api.json .
CMD ["sh", "-c", "python3 main.py --listen 0.0.0.0 & python3 -u handler.py"]