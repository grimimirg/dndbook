FROM node:20-alpine as build

WORKDIR /app

# Build arguments for Vite environment variables
ARG VITE_API_URL=""
ARG VITE_MOCK_DATA="false"
ARG VITE_AVAILABLE_LOCALES="en,it,de,es,fr"
ARG VITE_POSTS_PER_PAGE="10"
ARG VITE_POST_PREVIEW_LIMIT="200"

# Set as environment variables for the build
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_MOCK_DATA=${VITE_MOCK_DATA}
ENV VITE_AVAILABLE_LOCALES=${VITE_AVAILABLE_LOCALES}
ENV VITE_POSTS_PER_PAGE=${VITE_POSTS_PER_PAGE}
ENV VITE_POST_PREVIEW_LIMIT=${VITE_POST_PREVIEW_LIMIT}

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM nginx:alpine

ARG DEPLOYMENT_MODE=standalone

COPY --from=build /app/dist /usr/share/nginx/html

# Copy the appropriate nginx config based on deployment mode
RUN if [ "$DEPLOYMENT_MODE" = "homelab" ]; then \
        echo "Using homelab nginx config"; \
    else \
        echo "Using standalone nginx config"; \
    fi

COPY nginx.conf /tmp/nginx.standalone.conf
COPY nginx.homelab.conf /tmp/nginx.homelab.conf

RUN if [ "$DEPLOYMENT_MODE" = "homelab" ]; then \
        cp /tmp/nginx.homelab.conf /etc/nginx/conf.d/default.conf; \
    else \
        cp /tmp/nginx.standalone.conf /etc/nginx/conf.d/default.conf; \
    fi

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]