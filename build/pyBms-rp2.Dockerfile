FROM debian:bullseye-slim

ENV TERM=xterm DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
  apt-get install -y git-core python3-dev build-essential autoconf libtool libffi-dev pkg-config \
  cmake gcc-arm-none-eabi libnewlib-arm-none-eabi build-essential

RUN set -x && groupadd -g 1000 mpy && \
  useradd mpy -u 1000 -g 1000 -s /bin/bash --no-create-home && \
  mkdir /mpy/ && chown -Rf mpy:mpy /mpy/

USER mpy
WORKDIR /mpy/

RUN git clone --depth=1 https://github.com/micropython/micropython.git

RUN cd micropython && make -C mpy-cross

RUN cd /mpy/micropython && make -C ports/rp2 submodules && cd /mpy/micropython/ports/rp2 && make

COPY platforms/canbed_dual/pyBms.py /mpy/micropython/ports/rp2/modules/pyBms.py
COPY platforms/canbed_dual/typing.py /mpy/micropython/ports/rp2/modules/typing.py
COPY battery /mpy/micropython/ports/rp2/modules/battery/
COPY bms /mpy/micropython/ports/rp2/modules/bms/
COPY hal /mpy/micropython/ports/rp2/modules/hal/
COPY emulator /mpy/micropython/ports/rp2/modules/emulator/

RUN cd /mpy/micropython/ports/rp2 && make
