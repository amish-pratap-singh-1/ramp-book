FROM postgres:18.3-bookworm

ENV LANG=en_US.utf8

COPY ./init /docker-entrypoint-initdb.d/

EXPOSE 5432