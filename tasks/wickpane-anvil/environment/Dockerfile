FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb AS py

FROM public.ecr.aws/docker/library/golang:1.24-bookworm@sha256:1a6d4452c65dea36aac2e2d606b01b4a029ec90cc1ae53890540ce6173ea77ac

WORKDIR /app

COPY --from=py /usr/local /usr/local
COPY offpack/wheels /opt/wheels
RUN ldconfig \
    && ln -sf /usr/local/bin/python3 /usr/bin/python3 \
    && python3 -m venv /opt/verifier \
    && /opt/verifier/bin/pip install --no-cache-dir --no-index --find-links=/opt/wheels \
         pytest==8.4.1 pytest-json-ctrf==0.3.5 pygments==2.10.0 \
         pluggy==1.6.0 iniconfig==2.3.0 packaging==26.3 asciinema==2.4.0 \
    && ln -sf /opt/verifier/bin/asciinema /usr/local/bin/asciinema \
    && rm -rf /opt/wheels

COPY offpack/debs /tmp/debs
RUN set +e \
    && for i in 1 2 3 4 5 6; do \
         dpkg -i --force-depends /tmp/debs/*.deb >/dev/null 2>&1; \
         dpkg --configure -a >/dev/null 2>&1; \
       done \
    && set -e \
    && tmux -V \
    && rm -rf /tmp/debs \
    && ln -sf /usr/local/go/bin/go /usr/local/bin/go \
    && ln -sf /usr/local/go/bin/gofmt /usr/local/bin/gofmt

ENV PATH="/usr/local/go/bin:/usr/local/bin:/app/bin:/usr/bin:/bin:${PATH}"
ENV GOPROXY=off
ENV GOTOOLCHAIN=local
ENV GOFLAGS=-mod=mod

COPY go.mod /app/go.mod
COPY Makefile /app/Makefile
COPY vatmill /app/vatmill
COPY spoolkit /app/spoolkit
COPY wicksrc /app/wicksrc
COPY pantryc /app/pantryc
COPY celltyp /app/celltyp
COPY millhint /app/millhint
COPY bindnote /app/bindnote
COPY crumbay /app/crumbay
COPY shardops /app/shardops
COPY loomwell /app/loomwell

RUN mkdir -p /app/bin \
    && make -C /app ship

WORKDIR /app
