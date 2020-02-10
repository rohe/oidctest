FROM ubuntu:18.04
MAINTAINER hans.zandbelt@oidf.org

RUN apt-get clean && apt-get --fix-missing update
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y git ntp curl
RUN apt-get update && apt-get install -y gnupg
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -

RUN apt-get update && apt-get install -y nodejs apache2

ENV SRCDIR /usr/local/src
ENV INSTDIR node-oidc-provider
ENV SUBDIR ${SRCDIR}/${INSTDIR}

WORKDIR ${SRCDIR}

ENV VERSION_NODE_OP   tags/v6.20.1

RUN git clone https://github.com/panva/node-oidc-provider.git
RUN cd node-oidc-provider && git checkout ${VERSION_NODE_OP} && cd -
RUN cd ${INSTDIR} && npm install && cd -

COPY docker/op/apache-ssl.conf /etc/apache2/sites-available/ssl.conf
COPY docker/op/cert.pem /etc/apache2/
COPY docker/op/key.pem /etc/apache2/

RUN a2enmod headers && a2enmod ssl && a2enmod proxy && a2enmod proxy_http && a2ensite ssl

COPY docker/op/run.sh ${SUBDIR}/

WORKDIR ${SUBDIR}
ENTRYPOINT ["./run.sh"]
