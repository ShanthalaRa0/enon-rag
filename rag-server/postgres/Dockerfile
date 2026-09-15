FROM postgres:16-alpine

COPY init/ /docker-entrypoint-initdb.d/
COPY startup.sh /usr/local/bin/startup.sh

RUN chmod +x /usr/local/bin/startup.sh

ENTRYPOINT ["/usr/local/bin/startup.sh"]