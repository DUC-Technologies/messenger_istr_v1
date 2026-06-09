IMAGE_NAME="fastapi-template"
IMAGE_TAG="0.01"
HOST_PORT="81"
CONTAINER_PORT="81"

# Сборка Docker-образа
docker build -t "$IMAGE_NAME":"$IMAGE_TAG" .

# Запуск контейнера
docker run -p "$HOST_PORT":"$CONTAINER_PORT" -d "$IMAGE_NAME":"$IMAGE_TAG"
