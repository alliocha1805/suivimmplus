# Use a lightweight Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all necessary files
COPY main.py .
COPY debut.txt .
COPY fin.txt .
COPY roster.json .


# Command to run the bot
CMD ["python", "main.py"]
