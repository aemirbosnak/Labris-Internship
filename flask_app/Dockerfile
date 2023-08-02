FROM python:3

# Set the working directory inside the container
WORKDIR /app

COPY cagri.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --cert /etc/ssl/certs/cagri.pem --timeout=1000 --no-cache-dir -r requirements.txt

# Copy Flask application code into the container
COPY . .

# Expose the port
EXPOSE 5000

# Command to run Flask app 
# TODO make it run with uwsgi
CMD ["flask", "run", "--host", "0.0.0.0"]

