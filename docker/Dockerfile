FROM python:3.10.4-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 한국 시간대 설정
RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

COPY . .

CMD [ "python", "main.py" ]