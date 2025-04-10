# FROM python:3.9-alpine

# # Install Bash
# RUN apk add --no-cache bash

# WORKDIR /app

# # Copy code and scripts
# COPY . .

# # RUN apt-get update && apt-get install -y \\
# #     mpg321 \\
# #     && apt-get clean \\
# #     && rm -rf /var/lib/apt/lists/*

# RUN [ "apt-get", "update"]
# RUN [ "apt-get", "install", "-y", "mpg321"]
# # Make script executable
# RUN chmod +x scripts/run_docker.sh

# # ENV PYTHONPATH=/app:\$PYTHONPATH


# EXPOSE 8000

# CMD ["/bin/bash", "-c", "./scripts/run_docker.sh && uvicorn backend:app --host 0.0.0.0 --port 8000 --reload"]

# # Run the script during build
# # RUN /app/scripts/run_docker.sh



# # CMD ["uvicorn", "backend:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]


FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bash \
    mpg321

WORKDIR /app


RUN apt-get update && apt-get install -y \
    git \
    bash \
    mpg321 \
    && apt-get clean
# Copy files
COPY . .

# Make script executable
# RUN pip3 install git+https://github.com/username/aipolabs.git

RUN pip3 install -r requirements.txt

EXPOSE 8000

# Install Python dependencies
# RUN "/bin/bash -c ./scripts/run_docker.sh"

CMD ["uvicorn", "backend:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]


# sudo docker build -t myapp .
# sudo docker run -p 8000:8000 myapp