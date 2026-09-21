FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb AS py

FROM public.ecr.aws/docker/library/rust:1.85-slim@sha256:9f841bbe9e7d8e37ceb96ed907265a3a0df7f44e3737d0b100e7907a679acb36

WORKDIR /app

COPY --from=py /usr/local /usr/local
COPY vatpkg/wheels /opt/wheels
RUN ldconfig \
    && ln -sf /usr/local/bin/python3 /usr/bin/python3 \
    && python3 -m venv /opt/verifier \
    && /opt/verifier/bin/pip install --no-cache-dir --no-index --find-links=/opt/wheels \
         pytest==8.4.1 pytest-json-ctrf==0.3.5 pygments==2.10.0 \
         pluggy==1.6.0 iniconfig==2.3.0 packaging==26.3 asciinema==2.4.0 \
    && ln -sf /opt/verifier/bin/asciinema /usr/local/bin/asciinema \
    && rm -rf /opt/wheels

COPY vatpkg/debs /tmp/debs
RUN set +e \
    && for i in 1 2 3 4 5 6; do \
         dpkg -i --force-depends /tmp/debs/*.deb >/dev/null 2>&1; \
         dpkg --configure -a >/dev/null 2>&1; \
       done \
    && set -e \
    && tmux -V \
    && rm -rf /tmp/debs

ENV PATH="/usr/local/cargo/bin:/usr/local/bin:/app/bin:/usr/bin:/bin:${PATH}"

COPY stoke.sh /app/stoke.sh
COPY gaskcli /app/gaskcli
COPY rimcap /app/rimcap
COPY hopmat /app/hopmat
COPY lidpit /app/lidpit
COPY slipread /app/slipread
COPY loomkit /app/loomkit
COPY opscribe /app/opscribe
COPY buscards /app/buscards
COPY cardbak /app/cardbak
RUN mkdir -p /app/bin /app/mistwell /app/corkbay \
    && chmod +x /app/stoke.sh \
    && /app/stoke.sh \
    && /app/bin/gasketd bind \
    && /app/bin/gasketd cork || true

WORKDIR /app
