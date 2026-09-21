FROM public.ecr.aws/docker/library/golang:1.24-bookworm@sha256:1a6d4452c65dea36aac2e2d606b01b4a029ec90cc1ae53890540ce6173ea77ac

WORKDIR /app

RUN ln -sfn /app /app/environment

# Offline build: the pinned base already ships python3 3.11.2-1+b1. The
# remaining apt packages and the verifier wheels are vendored under apt-cache/
# and verifier-wheels/, so no build step needs the network.
COPY apt-cache /tmp/apt-cache
RUN dpkg -i /tmp/apt-cache/*.deb && rm -rf /tmp/apt-cache

RUN python3 -m venv --without-pip /opt/verifier

COPY verifier-wheels /tmp/wheels

RUN python3 -c "import zipfile, glob; [zipfile.ZipFile(w).extractall('/opt/verifier/lib/python3.11/site-packages') for w in glob.glob('/tmp/wheels/*.whl')]" \
    && printf '#!/opt/verifier/bin/python3\nimport sys\nfrom pytest import console_main\nif __name__ == "__main__":\n    sys.exit(console_main())\n' > /opt/verifier/bin/pytest \
    && chmod +x /opt/verifier/bin/pytest \
    && rm -rf /tmp/wheels

COPY go.mod /app/go.mod
COPY wk /app/wk
COPY stx /app/stx
COPY tab /app/tab
COPY specs /app/specs
COPY workloads /app/workloads

RUN mkdir -p /app/bin /app/stores /app/output \
    && cd /app && go build -o /app/bin/wrenkv ./wk \
    && chmod +x /app/bin/wrenkv
