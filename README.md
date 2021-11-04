_A web crowd counting interface. Post images, video, rtsp or webcam sreams._

---

## Presentation
 Makefile : Contains commands and variables for the projet.<br />
 |_ backend : **FastAPI** server, wraps the crowd counting models.<br />
 |_ frontend : Web interface in **Svelte**.<br />
 |_ Conf for 'reverse proxy' **nginx**

## Prerequisites
 - Install Docker and Docker-Compose locally.
 - Install Make.
 - Download the models : `make download-models`
 - Create artifacts `mv artifacts.sample artifacts` and replace with your variables.

## The micro-services

### Backend
 - Build backend in dev mode : `make backend-dev`.
 - Get in the container : `make backend-exec`.
 - Launch unit tests `make test`.

### Nginx
   -  Build nginx in dev mode : `make nginx-dev`. Only the 80 port is exposed.
   - TODO: Create the prod target

### Frontend
  - Build frontend in dev mode : `make frontend-dev`. (En mode `dev`)
  - TODO: Create client side application for the prod
  - Go to http://localhost (with hot-reloading in dev mode)

## useful commands
 - launch everything `make dev`.
