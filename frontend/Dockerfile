FROM node:22.8-alpine AS build
WORKDIR /frontend
COPY package*.json ./
RUN npm install
COPY . .

ARG VUE_APP_CELESTIA_RPC_URL
ARG VUE_APP_FETCH_RPC_URL
ARG VUE_APP_TELEGRAM_BOT_LINK
ARG VUE_APP_BACKEND_URL

RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /frontend/dist /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]