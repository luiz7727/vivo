# Dashboard
FROM node:18-alpine
RUN apk update
RUN apk add git
RUN git clone https://www.github.com/luiz7727/vivo-front app
WORKDIR /app
RUN git pull
RUN npm install
RUN npm i -g serve
RUN npm run build
EXPOSE 3000
CMD [ "serve", "-s", "dist" ]