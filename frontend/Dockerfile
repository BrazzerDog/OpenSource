# Build stage
FROM node:16-alpine as build

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm install

# Копируем исходники
COPY . .

# Собираем приложение
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 