FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY factory_calculator.py .

COPY . .

EXPOSE 8050

CMD ["python", "app.py"]
