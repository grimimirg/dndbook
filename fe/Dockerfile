FROM node:20-alpine as build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM nginx:alpine

ARG DEPLOYMENT_MODE=standalone

COPY --from=build /app/dist /usr/share/nginx/html

# Copy the appropriate nginx config based on deployment mode
COPY nginx${DEPLOYMENT_MODE:+.homelab}.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]