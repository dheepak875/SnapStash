FROM nginx:alpine

# Generate self-signed SSL certificate
RUN apk add --no-cache openssl && \
    mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 3650 \
      -newkey rsa:2048 \
      -keyout /etc/nginx/ssl/snapstash.key \
      -out /etc/nginx/ssl/snapstash.crt \
      -subj "/C=US/ST=Local/L=Local/O=SnapStash/CN=snapstash.local" && \
    apk del openssl

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443
