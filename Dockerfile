FROM python:3.11-alpine
RUN apk add --no-cache gcc musl-dev
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN rm -rf /root/.cache /var/cache/apk/*
COPY . .

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
