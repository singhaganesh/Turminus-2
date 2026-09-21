FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb AS py

FROM public.ecr.aws/docker/library/gcc:13-bookworm@sha256:930f2ebe239275fa67226654cb79273ea34eee672ae61c8a39f689c37fb7ac5c

WORKDIR /app

# Offline Python + pytest. No apt-get / no network.
COPY --from=py /usr/local /usr/local
COPY vendor/wheels /opt/wheels
RUN ldconfig \
    && ln -sf /usr/local/bin/python3 /usr/bin/python3 \
    && ln -sf /usr/local/bin/python3 /usr/bin/python \
    && python3 -m venv /opt/verifier \
    && /opt/verifier/bin/pip install --no-cache-dir --no-index --find-links=/opt/wheels \
         pytest==8.4.1 pytest-json-ctrf==0.3.5 pygments==2.17.2 \
         pluggy==1.6.0 iniconfig==2.3.0 packaging==26.3 asciinema==2.4.0 \
    && ln -sf /opt/verifier/bin/asciinema /usr/local/bin/asciinema \
    && rm -rf /opt/wheels

# Tiny pinned .debs for tmux.
COPY vendor/debs /tmp/debs
RUN set +e \
    && for i in 1 2 3 4 5 6; do \
         dpkg -i --force-depends /tmp/debs/*.deb >/dev/null 2>&1; \
         dpkg --configure -a >/dev/null 2>&1; \
       done \
    && set -e \
    && tmux -V \
    && rm -rf /tmp/debs

ENV PATH="/opt/verifier/bin:/app/bin:/app:${PATH}"

COPY . /app

RUN mkdir -p /srv \
    && ln -sfn /app /srv/anvil \
    && mkdir -p /app/bin /app/var /app/fixtures \
    && make -C /app reforge

WORKDIR /app
