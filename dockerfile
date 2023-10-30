# Use an official Python runtime as a base image
FROM python:3.11-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Git as it's needed for the repository cloning and updating
RUN apt-get update && apt-get install -y git

# Make port 80 available to the world outside this container
EXPOSE 8080

# Define environment variable for FastAPI to run on port 8080
ENV UVICORN_CMD="uvicorn main:app --host 0.0.0.0 --port 8080"

# Run the command to start uvicorn
ENTRYPOINT ["sh", "-c", "$UVICORN_CMD"]
