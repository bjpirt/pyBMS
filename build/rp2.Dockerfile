FROM micropython/build-micropython-arm

ARG MPY_VERSION=v1.19
ARG BOARD
ARG BMS_BOARD
ARG MAIN

WORKDIR /code

RUN git clone --depth=1 -b $MPY_VERSION https://github.com/micropython/micropython.git /code

RUN make -C mpy-cross && \
  make -C ports/rp2 submodules && \
  cd /code/ports/rp2 && \
  make

COPY platforms/micropython/typing.py /code/ports/rp2/modules/typing.py
COPY battery /code/ports/rp2/modules/battery/
COPY bms /code/ports/rp2/modules/bms/
COPY hal /code/ports/rp2/modules/hal/
COPY emulator /code/ports/rp2/modules/emulator/
COPY config_json.py /code/ports/esp32/modules/config_json.py
COPY platforms/rp2/${BMS_BOARD}/${MAIN}.py /code/ports/rp2/modules/main.py

RUN cd /code/ports/rp2 && \
  make && \
  mv /code/ports/rp2/build-${BOARD}/firmware.uf2 /code/ports/rp2/build-${BOARD}/${MAIN}.uf2 
