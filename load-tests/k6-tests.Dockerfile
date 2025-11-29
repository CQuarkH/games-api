FROM alpine:3.19

# Instalar k6 y dependencias
RUN apk add --no-cache \
    ca-certificates \
    wget \
    bash \
    curl

# Instalar k6
RUN wget -q -O /tmp/k6.tar.gz https://github.com/grafana/k6/releases/download/v0.48.0/k6-v0.48.0-linux-amd64.tar.gz && \
    tar -xzf /tmp/k6.tar.gz -C /usr/local/bin --strip-components=1 k6-v0.48.0-linux-amd64/k6 && \
    rm /tmp/k6.tar.gz && \
    chmod +x /usr/local/bin/k6

# Verificar instalación
RUN k6 version

WORKDIR /scripts

# Usar bash como shell por defecto
ENTRYPOINT ["/bin/bash"]
