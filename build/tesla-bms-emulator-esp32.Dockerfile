FROM espressif/idf:release-v4.4

ARG MPY_VERSION=v1.19

WORKDIR /code

RUN git clone --depth=1 -b $MPY_VERSION https://github.com/micropython/micropython.git /code && \
  git submodule init lib/berkeley-db-1.xx && \
  git submodule update

SHELL ["/bin/bash", "-c"]
RUN . /opt/esp/idf/export.sh && \
  make -C mpy-cross && \
  make -C ports/esp32 submodules && \
  cd /code/ports/esp32 && \
  make && \
  rm -rf /code/ports/esp32/build-GENERIC

COPY platforms/micropython/typing.py /code/ports/esp32/modules/typing.py
COPY battery /code/ports/esp32/modules/battery/
COPY bms /code/ports/esp32/modules/bms/
COPY hal /code/ports/esp32/modules/hal/
COPY emulator /code/ports/esp32/modules/emulator/
COPY platforms/wemos-esp32/teslaBmsEmulator.py /code/ports/esp32/modules/main.py

RUN . /opt/esp/idf/export.sh && \
  cd /code/ports/esp32 && \
  make
