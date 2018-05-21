FROM ubuntu:16.04
MAINTAINER hans.zandbelt@oidf.org

RUN apt-get clean && apt-get --fix-missing update
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python3-dev
RUN apt-get update && apt-get install -y git ntp psmisc python3-pytest

ENV SRCDIR /usr/local/src
ENV INSTDIR oidf
ENV SUBDIR ${SRCDIR}/${INSTDIR}/oidc_op

WORKDIR ${SRCDIR}

#ENV PYOIDC_VERSION=tags/v0.14.0
#RUN git clone https://github.com/OpenIDC/pyoidc.git
#RUN cd pyoidc && git fetch origin && git checkout ${PYOIDC_VERSION} -b temp
#COPY docker/op_test/pyoidc.patch pyoidc.patch
#RUN cd pyoidc && patch -p1 < ../pyoidc.patch
#RUN cd pyoidc && python3 setup.py install

RUN git clone https://github.com/openid-certification/otest.git
RUN cd otest && python3 setup.py install && cd -

RUN mkdir oidctest
COPY . ${SRCDIR}/oidctest/
RUN cd oidctest && python3 setup.py install && cd -
RUN cd oidctest/tests && python3 -m pytest -x && cd -

RUN oidc_setup.py ${SRCDIR}/oidctest ${INSTDIR}
COPY docker/op_test/cert.pem ${SUBDIR}/certs/
COPY docker/op_test/key.pem ${SUBDIR}/certs/
COPY docker/op_test/config.py ${SUBDIR}/
COPY docker/op_test/tt_config.py ${SUBDIR}/

COPY docker/op_test/https%3A%2F%2Fop%3A4433 ${SUBDIR}/entities/https%3A%2F%2Fop%3A4433
COPY docker/op_test/assigned_ports.json ${SUBDIR}/
COPY docker/op_test/my_jwks_60003.json ${SUBDIR}/static/jwks_60003.json

COPY docker/op_test/run.sh ${SUBDIR}/

WORKDIR ${SUBDIR}
ENTRYPOINT ["./run.sh"]
