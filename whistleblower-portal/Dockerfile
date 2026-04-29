# Usar una imagen base específica y reducida (Alpine) para minimizar vulnerabilidades.
# NUNCA usar la etiqueta 'latest' para pasar las políticas de Trivy / ValidatingPolicies.
FROM python:3.8

# Definir variables de entorno de Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

# Establecer el directorio de trabajo
WORKDIR /app

# Crear un usuario no root para cumplir con la política 'runAsNonRoot: true'
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Actualizar el sistema operativo base y limpiar paquetes vulnerables
RUN apk upgrade --no-cache && \
    pip install --no-cache-dir --upgrade pip setuptools wheel

# Instalar las dependencias de Python como usuario root, pero en un directorio temporal 
# o copiarlas posteriormente. Para Alpine, a veces se requiere build-base si hay dependencias C.
# En este caso Flask es puro Python.
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && \
    # Eliminar paquetes sensibles o de desarrollo que no se requieren en producción para evitar CVES.
    pip uninstall -y setuptools wheel pip

# Copiar el código fuente de la aplicación
COPY app.py /app/

# Cambiar el propietario de los archivos al nuevo usuario y grupo
RUN chown -R appuser:appgroup /app

# Cambiar al usuario no root antes de ejecutar la aplicación
USER appuser

# Exponer el puerto en el que correrá la app (8080)
EXPOSE 8080

# Comando para iniciar la aplicación de forma segura
CMD ["python", "app.py"]