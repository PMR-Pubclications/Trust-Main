# 1. Create Local Root CA
openssl genrsa -out localCA.key 4096
openssl req -x509 -new -nodes -key localCA.key -sha256 -days 365 -out localCA.crt -subj "/CN=TrustdaleLocalCA"

# 2. Create Server Certificate (for Trust backend)
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=trustdale.internal"
openssl x509 -req -in server.csr -CA localCA.crt -CAkey localCA.key -CAcreateserial -out server.crt -days 365 -sha256

# 3. Create Client Certificate (for AudioVideoEngine-CPP)
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=AudioVideoEngineClient"
openssl x509 -req -in client.csr -CA localCA.crt -CAkey localCA.key -CAcreateserial -out client.crt -days 365 -sha256
