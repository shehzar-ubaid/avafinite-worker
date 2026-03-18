FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# System settings
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git python3-pip python3-dev ffmpeg libgl1-mesa-glx libglib2.0-0 wget

# Install ComfyUI
WORKDIR /app
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir runpod 

# Install Custom Nodes
WORKDIR /app/custom_nodes
RUN git clone https://github.com/AlekPet/ComfyUI_Custom_Nodes_AlekPet.git || true
RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git || true
RUN git clone https://github.com/jovandant/ComfyUI-VideoHelperSuite.git || true

# Copy Serverless files
WORKDIR /app
COPY handler.py .
COPY workflow_api.json . 

# Expose port (testing ke liye useful hai)
EXPOSE 8188

# ComfyUI aur Handler ko ek saath chalane ka sahi tareeqa
CMD ["sh", "-c", "python3 main.py --listen 0.0.0.0 & python3 -u handler.py"]