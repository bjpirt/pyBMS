MAIN = pyBms
PLATFORM = esp32
BMS_BOARD = wemos-d1
BOARD = GENERIC
FIRMWARE_FORMAT = bin

.PHONY: test
test:
	python -m unittest --verbose

.PHONY: integration-test
integration-test:
	python -m unittest discover -p '*integration*' --verbose 

.PHONY: module-fake-serial
module-fake-serial:
	socat  -d -d pty,rawer,echo=0,link=port1-end-a pty,rawer,echo=0,link=port1-end-b

.PHONY: pack-fake-serial
pack-fake-serial:
	socat  -d -d pty,rawer,echo=0,link=port1-end-a pty,rawer,echo=0,link=port1-end-b &
	socat  -d -d pty,rawer,echo=0,link=port2-end-a pty,rawer,echo=0,link=port2-end-b &
	socat  -d -d pty,rawer,echo=0,link=port3-end-a pty,rawer,echo=0,link=port3-end-b &

.PHONY: kill-socat
kill-socat:
	killall socat

.PHONY: build-tesla-bms-emulator-rp2
build-tesla-bms-emulator-rp2: MAIN = teslaBmsEmulator
build-tesla-bms-emulator-rp2: build-rp2

.PHONY: build-pyBms-rp2
build-pyBms-rp2: build-rp2

.PHONY: build-tesla-bms-emulator-esp32
build-tesla-bms-emulator-esp32: MAIN = teslaBmsEmulator
build-tesla-bms-emulator-esp32: build

.PHONY: build-pyBms-esp32
build-pyBms-esp32: build

.PHONY: build-rp2
build-rp2: PLATFORM = rp2
build-rp2: BOARD = PICO
build-rp2: BMS_BOARD = pico
build-rp2: FIRMWARE_FORMAT = uf2
build-rp2: build

.PHONY: build-conf
build-conf:
	scripts/data_to_py.py config.json config_json.py || scripts/data_to_py.py config.default.json config_json.py

.PHONY: build
build: build-conf
	rm -f ./build/out/${MAIN}.${PLATFORM}.${BMS_BOARD}.${FIRMWARE_FORMAT}
	docker build -f build/${PLATFORM}.Dockerfile --build-arg BOARD=${BOARD} --build-arg BMS_BOARD=${BMS_BOARD} --build-arg MAIN=${MAIN} -t pybms-build-${PLATFORM} .
	docker cp "$$(docker create --name tc pybms-build-${PLATFORM}):/code/ports/${PLATFORM}/build-${BOARD}/${MAIN}.${FIRMWARE_FORMAT}" ./build/out/${MAIN}.${PLATFORM}.${BMS_BOARD}.${FIRMWARE_FORMAT} && docker rm tc

.PHONY: flash-tesla-bms-emulator-rp2
flash-tesla-bms-emulator-rp2: build-tesla-bms-emulator-rp2
	cp ./build/out/tesla-bms-emulator.uf2 /Volumes/RPI-RP2/tesla-bms-emulator.uf2

.PHONY: flash-pyBms-rp2
flash-pyBms-rp2: build-pyBms-rp2
	cp ./build/out/pybms.uf2 /Volumes/RPI-RP2/pybms.uf2

.PHONY: flash-tesla-bms-emulator-esp32
flash-tesla-bms-emulator-esp32: build-tesla-bms-emulator-esp32
	esptool.py -c esp32 -b 921600 write_flash -z 0x1000 build/out/tesla-bms-emulator-esp32.bin

.PHONY: flash-pyBms-esp32
flash-pyBms-esp32: build-pyBms-esp32
	esptool.py -c esp32 -b 921600 write_flash -z 0x1000 build/out/pyBms.esp32.wemos-d1.bin

.PHONY: wipe-rp2
wipe-rp2:
	cp ./scripts/flash_nuke.uf2 /Volumes/RPI-RP2/flash_nuke.uf2

.PHONY: wipe-esp32
wipe-esp32:
	esptool.py -c esp32 -b 921600 erase_flash

.PHONY: lint
lint:
	pylint --recursive=y battery bms emulator hal platforms
