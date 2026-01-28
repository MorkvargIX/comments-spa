FROM node:24-alpine

WORKDIR /app/frontend

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

CMD ["sh", "-c", "cp -r dist/* /shared/frontend && sleep infinity"]