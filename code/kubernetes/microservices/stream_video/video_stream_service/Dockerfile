FROM node:22.2.0

# The application directory
WORKDIR /app

COPY package*.json /app

RUN npm ci --omit=dev

COPY src /app/src

# this is just information not necessarilly used
EXPOSE 3000

CMD npm start