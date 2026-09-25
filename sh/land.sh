docker compose up -d
docker logs -f lightning-receiver-node
docker exec -it lightning-receiver-node lncli create
