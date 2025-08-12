# Use uma imagem Python oficial e leve como base
FROM python:3.11-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# --- ADICIONE ESTA LINHA ---
# Copia o script do worker para o diretório de trabalho /app
COPY worker.py .
COPY discord_bot.py .

# Copie todo o código da nossa aplicação
COPY ./Backend /app/Backend

# Comando para rodar a aplicação quando o contêiner iniciar
CMD ["uvicorn", "Backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]