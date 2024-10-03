FROM node:22.8-alpine AS build
WORKDIR /frontend
COPY package*.json ./
RUN npm install
COPY . .

ENV VUE_APP_BACKEND_URL=''

RUN npm run build

FROM caddy:2-alpine
COPY --from=build /frontend/dist /usr/share/caddy/html
COPY Caddyfile /etc/caddy/Caddyfile
EXPOSE 80 443
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
