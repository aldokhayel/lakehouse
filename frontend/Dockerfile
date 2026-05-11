# Dockerfile — Development image for the lakehouse Next.js frontend.
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
EXPOSE 3000
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=development
CMD ["npm", "run", "dev"]
