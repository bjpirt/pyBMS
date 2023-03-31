# pyBMS

A MicroPython battery management system for home energy storage using Tesla modules - Work in progress

This will run on an RP2040 or an ESP32 based module and is designed to communicate with the original BMS boards on a bank of Tesla Model S battery modules. It will communicate with a Victron system in order to build a home energy storage system.

Project goals:

- Well-architected
- Well-tested
- Runs on readily available hardware
- Easy to extend codebase for other battery modules

## Tesla Model S Modules

The initial implementation supports communicating with the OEM BMS on these modules. [See the docs for more details](./battery/tesla_model_s/README.md)

## Hardware

The basic requirements for hardware are:

- CAN Bus support (for Victron output)
- UART Support (612500 baud for Tesla BMS Comms)
- Runs MicroPython
- 4 x GPIO
- ADC (for current sensor)

Whilst the RP2040 chip does not directly support CAN Bus, there is [can2040](https://github.com/KevinOConnor/can2040) library using PIO that will enable this. It does support the serial communications directly. The ESP32 does have a native CAN port, however this is not currently supported by MicroPython. It is possible to drive an SPI based CAN transceiver from MicroPython using the [micropython-mcp2515](https://github.com/jxltom/micropython-mcp2515) project.

Currently I am using a [Canbed Dual](https://www.seeedstudio.com/CANBed-DUAL-RP2040-based-Arduino-CAN-Bus-dev-board-2-independent-CAN2-0-CAN-FD-p-5377.html), as this has an I2C based CAN transceiver which it should be possible to drive from MicroPython using the I2C support.

The ideal solution is to use an ESP32 once MicroPython supports CAN on that platform.

### Hardware options

- ESP32 Built-in CAN driver + transceiver (current preferred option)
- ESP32 + external CAN driver (e.g. MCP2515)
- RP2040 + external CAN driver (e.g. MCP2515)

## Supported Platforms

### Unix

This is designed to run on a regular Python distribution. Note that this doesn't support Victron CAN communication or current measurement. You can test this locally using socat (install via homebrew on a mac) by doing the following:

1. Create a fake serial port pair

```
make module-fake-serial
```

2. In one terminal, run the dummy Tesla BMS board

```
python platforms/cpython/teslaBmsEmulator.py ./port1-end-a 230400
```

3. In another terminal, run the pyBms code

```
python platforms/cpython/pyBms.py ./port1-end-b 230400
```

When you've finished, you can stop socat with `make kill-socat`

It's also possible to run pyBms from a desktop computer against a real Tesla Model S module or the emulator running on a RP2040 based board using this approach, just pass in the serial port and baud rate (612500) to the command above. Note this will need to support running at 612500 baud. Not all do - if you have a Raspberry Pi RP2040 based module, you can make your own with the following sketch:

```C
void setup() {
  Serial.begin(612500);
  Serial1.begin(612500);
}

void loop() {
  if(Serial1.available()){
    Serial.write(Serial1.read());
  }
  if(Serial.available()){
    Serial1.write(Serial.read());
  }
}
```

### Building firmware images

To build the emulator for the Canbed Dual platform (or other RP2040 based modules), run:

```
make build-tesla-bms-emulator-rp2
```

Which will produce `build/out/tesla-bms-emulator.uf2`. You can drag and drop this onto your RP2040 device as usual.

## To Do

- [x] Simulator for integration testing over socat virtual serial port
- [x] Cell balancing
- [x] Battery Management System controlling contactors
- [x] Hardware abstraction layer for GPIO
- [x] Communication error detection
- [x] Build script to generate image to flash
- [x] Platform support e.g. ESP32, RP2, etc with hardware details
- [x] Simulator running on physical devices
- [x] pyBms running on physical devices
- [x] Hardware abstraction layer for time
- [x] Hardware abstraction layer for Pin
- [x] Run against real hardware (real Tesla BMS boards with faked cells)
- [x] Run on ESP32 platform
- [x] CAN bus support (ESP32)
- [x] Victron CAN bus output
- [x] Static configuration file
- [x] Balance config
- [x] Battery capacity config
- [x] Alarms and warnings
- [x] State of charge from voltage
- [x] Dynamic configuration (web)
- [x] Data endpoint
- [x] Watchdog Timer
- [ ] Monitoring UI
- [ ] Configure over/under voltage into the Tesla BMS
- [ ] Configure over/under temperature into the Tesla BMS
- [ ] State of charge from current sensor
