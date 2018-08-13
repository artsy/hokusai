FROM nginx:latest

ADD https://github.com/Yelp/dumb-init/releases/download/v1.2.2/dumb-init_1.2.2_amd64 /usr/local/bin/dumb-init
RUN chmod +x /usr/local/bin/dumb-init

RUN mkdir /app
ADD . /app
WORKDIR /app

ENV PORT 80
EXPOSE 80

ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["nginx", "-g", "daemon off;"]

