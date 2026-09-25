docker compose up -d
docker logs -f lightning-receiver-node
docker exec -it lightning-receiver-node lncli create
docker exec -it lightning-receiver-node lncli addinvoice --amt=5000 --memo="Cloud Payout Sweep"

