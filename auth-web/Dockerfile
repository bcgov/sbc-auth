FROM node:16.14.2 as build-stage
WORKDIR /app
COPY ./package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.18.0 as production-stage

ARG VCS_REF="missing"
ARG BUILD_DATE="missing"

ENV VCS_REF=${VCS_REF}
ENV BUILD_DATE=${BUILD_DATE}

LABEL org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.build-date=${BUILD_DATE}

COPY nginx.conf /etc/nginx/nginx.conf
RUN mkdir /app
COPY --from=build-stage /app/dist /app
EXPOSE 8080:8080
CMD ["nginx", "-g", "daemon off;"]
