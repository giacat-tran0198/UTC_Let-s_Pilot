FROM node:lts-alpine as builder

WORKDIR /app
COPY package.json .
COPY yarn.lock .

RUN yarn
COPY . .
RUN yarn run build

FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
RUN mkdir -p /etc/nginx/certs
COPY ./https/tx_chat-certificate.crt /etc/nginx/certs
COPY ./https/tx_chat.key /etc/nginx/certs
COPY nginx.conf /etc/nginx/nginx.conf