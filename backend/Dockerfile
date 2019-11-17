FROM node:12-alpine

WORKDIR /usr/app

COPY package.json .
RUN yarn

COPY . .

RUN yarn migrate
RUN yarn seed