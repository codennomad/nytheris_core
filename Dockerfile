# Use uma imagem Python oficial e leve como base
FROM python:3.11-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código da nossa aplicação
COPY ./Backend /app/Backend

# Comando para rodar a aplicação quando o contêiner iniciar
# Escuta em todas as interfaces de rede (0.0.0.0) para ser acessível
CMD ["uvicorn", "Backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]