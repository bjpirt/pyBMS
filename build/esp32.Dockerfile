FROM espressif/idf:release-v4.4

# ARG MPY_VERSION=v1.19
ARG MPY_VERSION=esp32-can
ARG BOARD
ARG BMS_BOARD
ARG MAIN

WORKDIR /code

RUN git clone --depth=1 -b $MPY_VERSION https://github.com/FeroxTL/micropython-can.git /code && \
  git submodule init lib/berkeley-db-1.xx && \
  git submodule update

RUN . /opt/esp/idf/export.sh && \
  make -C mpy-cross && \
  make -C ports/esp32 submodules && \
  cd /code/ports/esp32 && \
  make && \
  rm -rf /code/ports/esp32/build-${BOARD}

COPY platforms/micropython/typing.py /code/ports/esp32/modules/typing.py
COPY platforms/micropython/__future__.py /code/ports/esp32/modules/__future__.py
COPY battery /code/ports/esp32/modules/battery/
COPY bms /code/ports/esp32/modules/bms/
COPY hal /code/ports/esp32/modules/hal/
COPY mqtt /code/ports/esp32/modules/mqtt/
COPY emulator /code/ports/esp32/modules/emulator/
COPY config.py /code/ports/esp32/modules/config.py
COPY config_json.py /code/ports/esp32/modules/config_json.py
COPY platforms/esp32/${BMS_BOARD}/${MAIN}.py /code/ports/esp32/modules/main.py
RUN curl -s -o /code/ports/esp32/modules/microdot.py https://raw.githubusercontent.com/miguelgrinberg/microdot/main/src/microdot.py

RUN . /opt/esp/idf/export.sh && \
  cd /code/ports/esp32 && \
  make && \
  mv /code/ports/esp32/build-${BOARD}/firmware.bin /code/ports/esp32/build-${BOARD}/${MAIN}.bin 
