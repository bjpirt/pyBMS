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

## To Do

- [x] Simulator for integration testing over socat virtual serial port
- [x] Cell balancing
- [x] Battery Management System controlling contactors
- [x] Hardware abstraction layer for GPIO
- [ ] Communication error detection
- [ ] Victron CAN bus output
- [ ] State of charge from current sensor
- [ ] Hardware abstraction layer for UART
- [ ] Hardware abstraction layer for CAN
- [ ] Hardware abstraction layer for RTC / Clock
- [ ] Simulator running on real devices
- [ ] Platform support e.g. ESP32, RP2, etc with hardware details
- [ ] Static configuration
- [ ] Dynamic configuration (serial / usb)
- [ ] Dynamic configuration (web)
