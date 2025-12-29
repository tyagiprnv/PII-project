# 1. Use a lightweight Python version
FROM python:3.10-slim

# 2. Set the working directory inside the box
WORKDIR /app

# 3. Copy your requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_lg

# 4. Copy all your code into the box
COPY . .

# 5. The command to start your app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]