ARG FRONTEND_PORT

#######################
# Step 1: Base target #
#######################
FROM node:12.2.0-alpine as base
RUN   apk update \
 &&   apk add ca-certificates wget \
 &&   update-ca-certificates

WORKDIR /app
COPY . .
RUN npm config set strict-ssl false #Do not check certificate, proxy fault
RUN npm install

# For production, see https://github.com/mikenikles/sapper-on-cloud-run/blob/master/Dockerfile
################################
# Step 2: "development" target #
################################
FROM base as dev
EXPOSE 5000
ENV HOST=0.0.0.0
ENV PORT=

CMD [ "npm", "run","dev" ]

################################
# Step 3:   "build" target     #
################################
FROM base as build
CMD ["npm", "run", "build"]
