FROM python:3.10-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Make app dir
RUN mkdir /app

# Set the working directory
WORKDIR /app

# Set PYTHONPATH to include the src directory
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Copy test and application code
COPY . .

# Set the command to keep the container alive
CMD ["tail", "-f", "/dev/null"]