FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

WORKDIR /app

COPY vendor/wheels /opt/wheels
RUN python3 -m venv /opt/verifier \
    && /opt/verifier/bin/pip install --no-cache-dir --no-index --find-links=/opt/wheels \
         pytest==8.4.1 pytest-json-ctrf==0.3.5 pygments==2.10.0 \
         pluggy==1.6.0 iniconfig==2.3.0 packaging==26.3 asciinema==2.4.0 \
    && ln -sf /opt/verifier/bin/asciinema /usr/local/bin/asciinema \
    && rm -rf /opt/wheels

COPY vendor/debs /tmp/debs
RUN set +e \
    && for i in 1 2 3 4 5 6; do \
         dpkg -i --force-depends /tmp/debs/*.deb >/dev/null 2>&1; \
         dpkg --configure -a >/dev/null 2>&1; \
       done \
    && set -e \
    && tmux -V \
    && rm -rf /tmp/debs

ENV PATH="/usr/local/bin:/app/bin:/app:${PATH}"
ENV PYTHONPATH="/app"

COPY pkga /app/pkga
COPY pkgb /app/pkgb
COPY pkgc /app/pkgc
COPY tracekit /app/tracekit
COPY archive /app/archive
RUN mkdir -p /app/bin && cp /app/tracekit/holdtrace_cli.sh /app/bin/holdtrace && chmod +x /app/bin/holdtrace \
    && chmod +x /app/tracekit/smoke/corpus_len.py

WORKDIR /app
