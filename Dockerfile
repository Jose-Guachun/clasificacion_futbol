# Usa una imagen oficial de Python 3.10
FROM python:3.10.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requisitos de Python al contenedor
COPY requirements.txt /app/

# Instala las dependencias desde el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código fuente al contenedor
COPY . /app/

# Expone el puerto 8000 donde Django correrá
EXPOSE 8000

# Comando para iniciar el servidor de desarrollo de Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
