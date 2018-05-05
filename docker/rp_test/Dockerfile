FROM ubuntu:16.04
MAINTAINER hans.zandbelt@oidf.org

RUN apt-get clean && apt-get --fix-missing update
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python3-dev
RUN apt-get update && apt-get install -y git ntp psmisc python3-pytest

ENV SRCDIR /usr/local/src
ENV INSTDIR oidf
ENV SUBDIR ${SRCDIR}/${INSTDIR}/oidc_cp_rplib

WORKDIR ${SRCDIR}

#ENV PYOIDC_VERSION=tags/v0.13.1
RUN git clone https://github.com/OpenIDC/pyoidc.git
RUN cd pyoidc && python3 setup.py install

RUN git clone https://github.com/openid-certification/otest.git
RUN cd otest && python3 setup.py install && cd -

RUN git clone https://github.com/OpenIDC/fedoidc.git
RUN cd fedoidc && python3 setup.py install && cd -

RUN mkdir oidctest
COPY . ${SRCDIR}/oidctest/
RUN cd oidctest && python3 setup.py install && cd -
RUN cd oidctest/tests && python3 -m pytest -x && cd -

RUN oidc_setup.py ${SRCDIR}/oidctest ${INSTDIR}
COPY docker/rp_test/cert.pem ${SUBDIR}/certs/
COPY docker/rp_test/key.pem ${SUBDIR}/certs/
COPY docker/rp_test/conf.py ${SUBDIR}/

COPY docker/rp_test/run.sh ${SUBDIR}/

WORKDIR ${SUBDIR}
ENTRYPOINT ["./run.sh"]
