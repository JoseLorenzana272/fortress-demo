# Imagen base definida específicamente (nunca 'latest')
FROM node:20.12.2-alpine3.19

# Establecer la directiva de entorno de producción
ENV NODE_ENV=production

# Usamos el directorio estándar e iniciamos el usuario root
WORKDIR /usr/src/app

# Copiar primero las dependencias para aprovechar la caché de Docker
COPY package*.json ./

# Instalar dependencias estrictamente para producción
# No usar npm install directamente así evitamos que cargue desarrollo
RUN npm ci --only=production

# Copiar el archivo del servidor
COPY server.js ./

# Asignar la propiedad oficial al usuario de 'node' por defecto de la imagen alpine
RUN chown -R node:node /usr/src/app

# Cambiar el contexto al usuario 'node' para NO ser root
USER node

# Exponer el puerto
EXPOSE 8080

# Iniciar la app
CMD ["npm", "start"]