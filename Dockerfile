FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04 [cite: 21]

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git python3-pip python3-dev ffmpeg libgl1-mesa-glx libglib2.0-0 wget

WORKDIR /app
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .
RUN pip3 install --no-cache-dir -r requirements.txt [cite: 22]
RUN pip3 install --no-cache-dir runpod requests

# Custom Nodes for Subtitles and Video
WORKDIR /app/custom_nodes
RUN git clone https://github.com/AlekPet/ComfyUI_Custom_Nodes_AlekPet.git || true [cite: 23]
RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git || true
RUN git clone https://github.com/jovandant/ComfyUI-VideoHelperSuite.git || true [cite: 24]

WORKDIR /app
# Files ko copy karna (Wildcard '*' lagaya hai taake agar file na ho to build fail na ho)
COPY handler.py* /app/handler.py
COPY workflow_api.json* /app/workflow_api.json

EXPOSE 8188

# Serverless Execution
CMD ["sh", "-c", "python3 main.py --listen 0.0.0.0 & python3 -u handler.py"]