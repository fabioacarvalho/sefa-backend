# Usa a imagem oficial do Python 3.10 como base
FROM python:3.10

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos necessários para o container
COPY . /app

# Copia a planilha para o container
COPY municipios.xlsx /app/

# Atualiza o pip e instala dependências corrigindo incompatibilidades
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expõe a porta 5000 para acessar a API
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]