# Use the official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 8080

# Run the app
CMD ["python", "app.py"]
