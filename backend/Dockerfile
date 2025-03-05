# Flask App
FROM python:3.8-alpine

# Install build dependencies
RUN apk add --no-cache gcc python3-dev musl-dev linux-headers

# Copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# Switch working directory
WORKDIR /app

# Install the dependencies and packages in the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy every content from the local file to the image
COPY . /app

# Install Gunicorn
RUN pip install gunicorn

# Command to run the application using Gunicorn
CMD ["gunicorn", "-w", "4", "-t", "120", "-b", "0.0.0.0:5000", "server:app"]