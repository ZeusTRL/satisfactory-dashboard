FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Ensure dev_dump.json is included
# (If you're doing selective copying, make sure this line includes dev_dump.json)
COPY dev_dump.json dev_dump.json

# Expose Dash app port
EXPOSE 8050

# Run the app
CMD ["python", "app.py"]
