FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04
WORKDIR /llm_server
ENV HF_TOKEN=${HF_TOKEN}
ENV PORT_NUMBER=6969
RUN apt update && apt install python3.10 -y 
RUN apt install python3-pip -y
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE $PORT_NUMBER
CMD ["gunicorn", "--bind", "127.1.1.1:6969" ,"run_server:app"]
