IMAGE_NAME="poker-$1"
CONTAINER_NAME=poker

for container in $(docker ps --filter "status=exited" --format '{{.Names}}' | grep -i "$CONTAINER_NAME" | awk '{print $1}');
    do
    echo "Removing Stopped $container"
    docker rm "$container"
done

docker run -p 8000:8000 -it \
    --mount type=bind,source="$(pwd)"/src,target=/opt/poker/src \
    --name "$IMAGE_NAME" "$CONTAINER_NAME"