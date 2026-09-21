FROM golang:1.22-bookworm@sha256:1f298b0c9fecdf504389a0329236f948cc04a566a2bb32337207cbaaa2f8177c

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3=3.11.2-1+b1 \
  python3-venv=3.11.2-1+b1 \
  && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/verifier
RUN /opt/verifier/bin/pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5
ENV PATH=/opt/verifier/bin:${PATH}




RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates=20230311+deb12u1 \
    python3=3.11.2-1+b1 \
    && rm -rf /var/lib/apt/lists/*

COPY src/. /app/
COPY data/fixtures /app/fixtures
COPY data/config /app/config

RUN go mod download \
    && go build -o /app/storesim ./cmd/storesim \
    && rm -rf /root/.cache/go-build

# Keep the toolchain on PATH for agent rebuilds and pytest subprocesses.
ENV PATH="/usr/local/go/bin:/app:${PATH}"
