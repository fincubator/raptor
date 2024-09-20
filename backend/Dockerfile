FROM python:3.11-slim
WORKDIR /backend

RUN apt-get update -y && apt-get install -y \
python3-dev build-essential

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000