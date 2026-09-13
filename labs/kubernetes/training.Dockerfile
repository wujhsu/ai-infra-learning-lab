FROM python:3.12.14-slim
WORKDIR /app
COPY labs/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY labs/tiny_model /app/labs/tiny_model
CMD ["python", "labs/tiny_model/train.py", "--steps", "100", "--output", "/results/tiny.pt"]
