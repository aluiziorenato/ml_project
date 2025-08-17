FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências primeiro (cache otimizado)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código do backend
COPY . .

# Variável para logs imediatos
ENV PYTHONUNBUFFERED=1

# Expor porta da API
# EXPOSE 8000
EXPOSE ${PORT:-8000}

# Comando padrão para desenvolvimento com hot-reload
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
