FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb AS py

FROM public.ecr.aws/docker/library/gcc:13-bookworm@sha256:930f2ebe239275fa67226654cb79273ea34eee672ae61c8a39f689c37fb7ac5c

WORKDIR /app

COPY --from=py /usr/local /usr/local
COPY hullpkg/wheels /opt/wheels
RUN ldconfig \
    && ln -sf /usr/local/bin/python3 /usr/bin/python3 \
    && python3 -m venv /opt/verifier \
    && /opt/verifier/bin/pip install --no-cache-dir --no-index --find-links=/opt/wheels \
         pytest==8.4.1 pytest-json-ctrf==0.3.5 pygments==2.10.0 \
         pluggy==1.6.0 iniconfig==2.3.0 packaging==26.3 asciinema==2.4.0 \
    && ln -sf /opt/verifier/bin/asciinema /usr/local/bin/asciinema \
    && rm -rf /opt/wheels

COPY hullpkg/debs /tmp/debs
RUN set +e \
    && for i in 1 2 3 4 5 6; do \
         dpkg -i --force-depends /tmp/debs/*.deb >/dev/null 2>&1; \
         dpkg --configure -a >/dev/null 2>&1; \
       done \
    && set -e \
    && tmux -V \
    && rm -rf /tmp/debs

ENV PATH="/usr/local/bin:/app/bin:/app:${PATH}"

COPY hull.sh /app/hull.sh
COPY flaxcli /app/flaxcli
COPY cordspin /app/cordspin
COPY chunkvat /app/chunkvat
COPY emitbay /app/emitbay
COPY differbay /app/differbay
COPY unreelkit /app/unreelkit
COPY vatnotes /app/vatnotes
COPY spoolbay /app/spoolbay

RUN mkdir -p /app/bin /app/cordwell \
    && chmod +x /app/hull.sh \
    && /app/hull.sh \
    && /app/bin/flaxcord spin /app/spoolbay/day /app/cordwell/live.pfl || true

WORKDIR /app
