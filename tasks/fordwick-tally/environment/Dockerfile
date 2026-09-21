FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

WORKDIR /app

COPY wheelurn/wheels /opt/wheels
COPY wheelurn/parts /opt/parts
COPY wheelurn/debs /tmp/debs

RUN set -eux; \
    cat /opt/parts/numpy/n.* > /tmp/numpy-2.2.6-cp313-cp313-manylinux2014_x86_64.whl; \
    cat /opt/parts/opencv/o.* > /tmp/opencv_python_headless-4.11.0.86-cp37-abi3-manylinux2014_x86_64.whl; \
    python3 -m venv /opt/verifier; \
    /opt/verifier/bin/pip install --no-cache-dir --no-index --find-links=/opt/wheels \
      pytest==8.4.1 pytest-json-ctrf==0.3.5 pygments==2.10.0 \
      pluggy==1.6.0 iniconfig==2.3.0 packaging==26.3 asciinema==2.4.0; \
    python3 -m pip install --no-cache-dir --no-index \
      /tmp/numpy-2.2.6-cp313-cp313-manylinux2014_x86_64.whl \
      /tmp/opencv_python_headless-4.11.0.86-cp37-abi3-manylinux2014_x86_64.whl \
      /opt/wheels/toml-0.10.2-py2.py3-none-any.whl; \
    ln -sf /opt/verifier/bin/asciinema /usr/local/bin/asciinema; \
    rm -rf /opt/wheels /opt/parts \
      /tmp/numpy-2.2.6-cp313-cp313-manylinux2014_x86_64.whl \
      /tmp/opencv_python_headless-4.11.0.86-cp37-abi3-manylinux2014_x86_64.whl

RUN set +e; \
    for i in 1 2 3 4 5 6; do \
      dpkg -i --force-depends /tmp/debs/*.deb >/dev/null 2>&1; \
      dpkg --configure -a >/dev/null 2>&1; \
    done; \
    set -e; \
    tmux -V; \
    rm -rf /tmp/debs

ENV PATH="/usr/local/bin:/app:${PATH}"

COPY blot.py /app/blot.py
COPY tether.py /app/tether.py
COPY spout.py /app/spout.py
COPY spanwell.py /app/spanwell.py
COPY shown.mp4 /app/shown.mp4
COPY slipfold /app/slipfold
COPY wickpit /app/wickpit
COPY hopcard /app/hopcard
COPY kiln /app/kiln
RUN mkdir -p /app/inkwell /app/varnish \
    && chmod +x /app/spanwell.py /app/wickpit/touchcue.py /app/kiln/bake.sh \
    && /app/kiln/bake.sh

WORKDIR /app
