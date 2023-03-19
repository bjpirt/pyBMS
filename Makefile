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
build-tesla-bms-emulator-rp2:
	rm -f ./build/out/tesla-bms-emulator-rp2.uf2
	docker build -f build/tesla-bms-emulator-rp2.Dockerfile -t bms-emulator-build-rp2 .
	docker cp $$(docker create --name tc bms-emulator-build-rp2):/mpy/micropython/ports/rp2/build-PICO/firmware.uf2 ./build/out/tesla-bms-emulator-rp2.uf2 && docker rm tc

.PHONY: build-pyBms-rp2
build-pyBms-rp2:
	rm -f ./build/out/pybms-rp2.uf2
	docker build -f build/pyBms-rp2.Dockerfile -t pybms-build-rp2 .
	docker cp $$(docker create --name tc pybms-build):/mpy/micropython/ports/rp2/build-PICO/firmware.uf2 ./build/out/pybms-rp2.uf2 && docker rm tc

.PHONY: build-tesla-bms-emulator-esp32
build-tesla-bms-emulator-esp32:
	rm -f ./build/out/tesla-bms-emulator-esp32.bin
	docker build -f build/tesla-bms-emulator-esp32.Dockerfile --progress=plain -t bms-emulator-build-esp32 .
	docker cp $$(docker create --name tc bms-emulator-build-esp32):/code/ports/esp32/build-GENERIC/firmware.bin ./build/out/tesla-bms-emulator-esp32.bin && docker rm tc
	# docker cp $$(docker create --name tc bms-emulator-build-esp32):/code/ports/esp32/build-GENERIC/bootloader/bootloader.bin ./build/out/tesla-bms-emulator-esp32.bootloader.bin && docker rm tc
	# docker cp $$(docker create --name tc bms-emulator-build-esp32):/code/ports/esp32/build-GENERIC/partition_table/partition-table.bin ./build/out/tesla-bms-emulator-esp32.partition-table.bin && docker rm tc
	# docker cp $$(docker create --name tc bms-emulator-build-esp32):/code/ports/esp32/build-GENERIC/firmware.bin ./build/out/tesla-bms-emulator-esp32.firmware.bin && docker rm tc

.PHONY: build-pyBms-esp32
build-pyBms-esp32:
	rm -f ./build/out/pybms-esp32.bin
	docker build -f build/pyBms-esp32.Dockerfile -t pybms-build-esp32 .
	docker cp $$(docker create --name tc pybms-build-esp32):/code/ports/esp32/build-GENERIC/firmware.bin ./build/out/pybms-esp32.bin && docker rm tc

.PHONY: flash-tesla-bms-emulator-rp2
flash-tesla-bms-emulator-rp2: build-tesla-bms-emulator-rp2
	cp ./build/out/tesla-bms-emulator.uf2 /Volumes/RPI-RP2/tesla-bms-emulator.uf2

.PHONY: flash-pyBms-rp2
flash-pyBms-rp2: build-pyBms-rp2
	cp ./build/out/pybms.uf2 /Volumes/RPI-RP2/pybms.uf2

.PHONY: flash-tesla-bms-emulator-esp32
flash-tesla-bms-emulator-esp32: build-tesla-bms-emulator-esp32
	# esptool.py -c esp32 -b 921600 --before default_reset --after hard_reset --chip esp32  write_flash --flash_mode dio --flash_size detect --flash_freq 40m 0x1000 build/out/tesla-bms-emulator-esp32.bootloader.bin 0x8000 build/out/tesla-bms-emulator-esp32.partition-table.bin 0x10000 build/out/tesla-bms-emulator-esp32.firmware.bin
	esptool.py -c esp32 -b 921600 write_flash -z 0x1000 build/out/tesla-bms-emulator-esp32.bin

.PHONY: flash-pyBms-esp32
flash-pyBms-esp32: build-pyBms-esp32
	esptool.py -c esp32 -b 921600 write_flash -z 0x1000 build/out/pyBms-esp32.bin

.PHONY: wipe-rp2
wipe-rp2:
	cp ./scripts/flash_nuke.uf2 /Volumes/RPI-RP2/flash_nuke.uf2

.PHONY: wipe-esp32
wipe-esp32:
	esptool.py -c esp32 -b 921600 erase_flash
