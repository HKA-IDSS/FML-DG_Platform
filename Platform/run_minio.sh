docker network create -d bridge minio-net

docker run \
   -p 9000:9000 \
   -p 9001:9001 \
   --name minio \
   -d \
   --network=minio-net \
   -v ~/minio/data:/data \
   -e "MINIO_ROOT_USER=MACTest" \
   -e "MINIO_ROOT_PASSWORD=MACTest9001" \
   quay.io/minio/minio server /data --console-address ":9001"

wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

./mc alias set minio http://localhost:9000 MACTest MACTest9001

./mc admin user add minio fastapi fastapi_secret




