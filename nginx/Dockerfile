#######################
# Step 1: Base target #
#######################
FROM nginx as base
ARG app_name
ARG app_ver

WORKDIR /home/nginx

COPY run.sh run.sh

EXPOSE 80/tcp
EXPOSE 443/tcp

RUN apt-get update --allow-releaseinfo-change -y

################################
# Step 2: "development" target #
################################
FROM base as development

COPY default-dev.template /etc/nginx/conf.d/default.template
RUN  [ -f "run.sh" ] && chmod +x  run.sh

CMD ["/home/nginx/run.sh"]

################################
# Step 3: "production" target #
################################
FROM base as production

# TODO

CMD ["/home/nginx/run.sh"]
