FROM nginx:alpine

COPY config /config/
COPY init.sh /init.sh

RUN ["chmod", "+x", "init.sh"]

ENTRYPOINT ["/init.sh"]

CMD /init.sh
