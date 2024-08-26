apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    libjpeg-dev \
    libpng-dev \
    libgl1 \
    ccache \
    cmake \
    curl \
    default-jdk \
    wget \
    gcc \
    build-essential \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa -y
apt-get update -y \
    && apt-get install -y python3-pip \
    && pip3 install --upgrade pip \
    && pip3 install pyem empy pyyaml
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 14.17.3
nvm use 14.17.3
pip install -r requirements.txt
npm install