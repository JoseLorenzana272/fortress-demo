# Imagen base definida específicamente (nunca 'latest')
FROM node:20.18.0-alpine3.19

# Establecer la directiva de entorno de producción
ENV NODE_ENV=production

# Usamos el directorio estándar e iniciamos el usuario root
WORKDIR /usr/src/app

# Copiar primero las dependencias para aprovechar la caché de Docker
COPY package*.json ./

# Actualizar npm globalmente a una versión limpia de CVES y dependencias vulnerables
RUN npm install -g npm@latest

# Instalar dependencias estrictamente para producción
# Dado que ya generamos el package-lock.json, podemos usar 'npm ci'
RUN npm ci --omit=dev

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