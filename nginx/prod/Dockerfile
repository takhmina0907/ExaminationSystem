FROM nginx:alpine

COPY config/app.template /config/
COPY init.sh /init.sh
COPY examinationsystem_me/examinationsystem_me_cert_chain.crt /etc/ssl/certs/
COPY examinationsystem_me/examinationsystem.key /etc/ssl/private/

RUN ["chmod", "+x", "init.sh"]

ENTRYPOINT ["/init.sh"]

CMD /init.sh
