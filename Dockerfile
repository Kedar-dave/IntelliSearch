# Use Python 3.11.7 as base image
FROM python:3.11.7

# Set working directory
WORKDIR /intellisearch

# Copy requirements.txt to the container
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install -r requirements.txt

# Copy .env file to the container
COPY .env .

# Copy the entire project directory to the container
COPY . .

# Expose port 9000
EXPOSE 9000

# Set FLASK_APP environment variable
# ENV FLASK_APP=flask_app.py

# Run Flask app
CMD ["python", "flask_app.py"]