# Usa una imagen base de Python
FROM python:3.10.0

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    wget unzip curl \
    gnupg

# Agregar la clave y repositorio de Google para instalar Chrome
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
    | tee /etc/apt/sources.list.d/google-chrome.list

# Instalar Google Chrome y ChromeDriver
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    chromium-driver

# Configura el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos necesarios dentro del contenedor
COPY . /app

# Instala las dependencias necesarias
RUN pip install -r requirements.txt

# Expón el puerto en el que FastAPI escuchará (por defecto 8000)
EXPOSE 8000

# Ejecuta el servidor de FastAPI
CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "8000"]
