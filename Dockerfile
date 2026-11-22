# Phlix Camera Upload
#
# A small server that receives the photos and videos the Phlix app uploads
# from an iPhone or iPad, and writes them into a folder of a Plex photo
# library. Setup guide: https://phlixapp.com/camera-upload/
#
# The program uses only the Python standard library, so the image is the
# Python base image plus one package.

FROM python:3.13-alpine

LABEL org.opencontainers.image.title="Phlix Camera Upload" \
      org.opencontainers.image.description="Receives the photos and videos that the Phlix app uploads from an iPhone or iPad and writes them into a folder of a Plex photo library." \
      org.opencontainers.image.url="https://phlixapp.com/camera-upload/" \
      org.opencontainers.image.source="https://github.com/jrl8085/phlix-camera-upload" \
      org.opencontainers.image.vendor="Phlix (phlixapp.com)" \
      org.opencontainers.image.licenses="LicenseRef-Proprietary"

# First take the fixes that Alpine has published since the base image was
# made. Then add the one package: the helper runs the openssl command once,
# on first start, to make its own TLS certificate.
RUN apk upgrade --no-cache && apk add --no-cache openssl

# PYTHONUNBUFFERED         log lines reach "docker logs" at once.
# PYTHONDONTWRITEBYTECODE  Python writes nothing into the image while it runs.
# PHLIX_CONTAINER          tells the helper that it runs from this image. It
#                          then refuses to start unless /photos and /config
#                          are real mounts, so uploads can never land inside
#                          the container and be lost with it.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PHLIX_CONTAINER=1

# There is no VOLUME line, on purpose. Docker would give an unmounted VOLUME
# an anonymous volume, the helper would see a mount, and the check above
# would pass by mistake.

WORKDIR /app
COPY phlix_upload/ ./phlix_upload/

EXPOSE 7459

# Ask the helper's own /healthz address for "ok". The check follows the
# PORT, TLS and BIND settings, and it does not verify the certificate: the
# helper's certificate is self-signed. Docker joins these lines into one
# Python command.
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import http.client, os, ssl, sys; \
env = os.environ; \
tls = env.get('TLS', 'on').strip().lower() not in ('0', 'false', 'no', 'off'); \
host = env.get('BIND', '').strip(); \
host = '127.0.0.1' if host in ('', '0.0.0.0') else host; \
port = int(float(env.get('PORT', '7459'))); \
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT); \
context.check_hostname = False; \
context.verify_mode = ssl.CERT_NONE; \
connection = http.client.HTTPSConnection(host, port, timeout=5, context=context) if tls else http.client.HTTPConnection(host, port, timeout=5); \
connection.request('GET', '/healthz'); \
response = connection.getresponse(); \
sys.exit(0 if response.status == 200 and response.read().strip() == b'ok' else 1)"

# There is no USER line, on purpose. The helper starts as root, then switches
# to the user who owns /photos (or to PUID and PGID) before it serves
# anything, so uploaded files belong to a normal user.
ENTRYPOINT ["python", "-m", "phlix_upload"]
