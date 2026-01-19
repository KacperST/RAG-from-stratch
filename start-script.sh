# docker run --rm -d --name elastic -p 9200:9200 \
#   -e ES_JAVA_OPTS="-Xms1g -Xmx1g" \
#   es-morfologik:8.19.4
docker compose up -d --build