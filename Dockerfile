FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git python3-pip ffmpeg libgl1-mesa-glx libglib2.0-0 wget curl

WORKDIR /app
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .

# 🔥 TORCH CUDA VERSION PEHLE INSTALL (yeh line sabse important hai)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Baaki requirements (ab torch wali lines hata di hain)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir runpod requests

# Custom Nodes
WORKDIR /app/custom_nodes
RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git || true
RUN git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git || true
RUN git clone https://github.com/AIGODLIKE/ComfyUI-SeedVR2.git || true
RUN git clone https://github.com/ShmuelRonen/ComfyUI-LatentSyncWrapper.git || true
RUN git clone https://github.com/kijai/ComfyUI-LivePortraitKJ.git || true
RUN git clone https://github.com/diodiogod/TTS-Audio-Suite.git || true
RUN git clone https://github.com/pythongosssss/ComfyUI-Custom-Nodes.git || true
   
WORKDIR /app
COPY handler.py .
COPY workflow_api.json .
RUN mkdir -p output

# Super fast startup
CMD ["sh", "-c", "python3 main.py --listen 0.0.0.0 --port 8188 --force-fp16 & python3 -u handler.py"]