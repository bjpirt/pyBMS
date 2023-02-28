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

## To Do

- [x] Simulator for integration testing over socat virtual serial port
- [x] Cell balancing
- [ ] Hardware abstraction layer for UART
- [ ] Hardware abstraction layer for RTC / Clock
- [ ] Simulator running on real devices
- [ ] Victron CAN bus output
- [ ] Battery Management system controlling contactors
- [ ] State of charge from current sensor
- [ ] Platform support e.g. ESP32, RP2, etc with hardware details
- [ ] Static configuration
- [ ] Dynamic configuration (serial / usb)
- [ ] Dynamic configuration (web)
