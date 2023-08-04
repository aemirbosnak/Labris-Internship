FROM python:3

WORKDIR /app

COPY ../cagri.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

COPY ../requirements.txt .
RUN pip install --cert /etc/ssl/certs/cagri.pem --timeout=1000 --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# TODO make it run with uwsgi
CMD ["flask", "run", "--host", "0.0.0.0"]
