FROM python:3.11-slim

WORKDIR /app

# Instalar matplotlib
RUN pip install --no-cache-dir matplotlib

# Copiar script
COPY generate_graphs.py .

# Punto de entrada
ENTRYPOINT ["python", "generate_graphs.py"]
