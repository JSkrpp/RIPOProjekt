FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    tk-dev \
    tcl-dev \
    libx11-6 \
    libx11-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "main.py"]