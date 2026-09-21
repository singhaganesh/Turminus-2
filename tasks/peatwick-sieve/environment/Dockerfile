FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb AS py

FROM public.ecr.aws/docker/library/ruby:3.3-slim-bookworm@sha256:e76733e94b3a5893e4a141024ef3a583dc10781dc24becebf74f9c9f9a33e3df

WORKDIR /app

COPY --from=py /usr/local /usr/local
COPY cratepit/wheels /opt/wheels
RUN ldconfig \
    && ln -sf /usr/local/bin/python3 /usr/bin/python3 \
    && python3 -m venv /opt/verifier \
    && /opt/verifier/bin/pip install --no-cache-dir --no-index --find-links=/opt/wheels \
         pytest==8.4.1 pytest-json-ctrf==0.3.5 pygments==2.10.0 \
         pluggy==1.6.0 iniconfig==2.3.0 packaging==26.3 asciinema==2.4.0 \
    && ln -sf /opt/verifier/bin/asciinema /usr/local/bin/asciinema \
    && rm -rf /opt/wheels

COPY cratepit/debs /tmp/debs
RUN set +e \
    && for i in 1 2 3 4 5 6; do \
         dpkg -i --force-depends /tmp/debs/*.deb >/dev/null 2>&1; \
         dpkg --configure -a >/dev/null 2>&1; \
       done \
    && set -e \
    && tmux -V \
    && rm -rf /tmp/debs

ENV PATH="/usr/local/bin:/app/bin:/usr/bin:/bin:${PATH}"

COPY knit.sh /app/knit.sh
COPY gaitmod /app/gaitmod
COPY joincue /app/joincue
COPY stillbay /app/stillbay
COPY fieldnotes /app/fieldnotes
COPY opside /app/opside
COPY snapurn /app/snapurn
COPY livefold /app/livefold
COPY lutcards /app/lutcards
COPY inkvat /app/inkvat

RUN mkdir -p /app/bin /app/inkvat \
    && chmod +x /app/knit.sh \
    && /app/knit.sh \
    && /app/bin/peatwick kindle || true

WORKDIR /app
