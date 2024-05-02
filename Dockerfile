FROM python:3.9.5-alpine3.13

WORKDIR /app

COPY src/ .

RUN apk --update add iperf3 && \
    rm -rf /var/cache/apk/*
    
RUN pip install -r requirements.txt && \
    rm requirements.txt

EXPOSE 9798

CMD ["python3", "exporter.py"]