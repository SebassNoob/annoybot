FROM redis:alpine

WORKDIR /data

# remove existing data
RUN rm -rf /dump.rdb

CMD ["redis-server", "--save", "''", "--appendonly", "no"]
