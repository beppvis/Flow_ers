FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Expose Vite port
EXPOSE 5173

# Run in development mode, listening on all interfaces
CMD ["npm", "run", "dev", "--", "--host"]
