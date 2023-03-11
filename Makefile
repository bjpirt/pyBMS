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
	rm -f ./build/out/tesla-bms-emulator.uf2
	docker build -f build/tesla-bms-emulator-rp2.Dockerfile -t bms-emulator-build .
	docker cp $$(docker create --name tc bms-emulator-build):/mpy/micropython/ports/rp2/build-PICO/firmware.uf2 ./build/out/tesla-bms-emulator.uf2 && docker rm tc

.PHONY: build-pyBms-rp2
build-pyBms-rp2:
	rm -f ./build/out/pybms.uf2
	docker build -f build/pyBms-rp2.Dockerfile -t pybms-build .
	docker cp $$(docker create --name tc pybms-build):/mpy/micropython/ports/rp2/build-PICO/firmware.uf2 ./build/out/pybms.uf2 && docker rm tc

.PHONY: flash-tesla-bms-emulator-rp2
flash-tesla-bms-emulator-rp2: build-tesla-bms-emulator-rp2
	cp ./build/out/tesla-bms-emulator.uf2 /Volumes/RPI-RP2/tesla-bms-emulator.uf2

.PHONY: flash-pyBms-rp2
flash-pyBms-rp2: build-pyBms-rp2
	cp ./build/out/pybms.uf2 /Volumes/RPI-RP2/pybms.uf2

.PHONY: nuke-rp2
nuke-rp2:
	cp ./scripts/flash_nuke.uf2 /Volumes/RPI-RP2/flash_nuke.uf2
