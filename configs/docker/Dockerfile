FROM alpine
RUN apk add --no-cache --upgrade curl
ADD set-ingest-actions.sh .
RUN chmod +x set-ingest-actions.sh
CMD ["/set-ingest-actions.sh"]
