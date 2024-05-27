FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
	apt-get -y install xpra && \
	apt-get -y --purge autoremove && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 10000
ENTRYPOINT ["xpra", "start",":100","--pulseaudio=no","--start-child=\"$*\"","--bind-tcp=0.0.0.0:10000","--no-daemon","--exit-with-children"]