def crc8(message: bytearray) -> int:
    seed: int = 0x07
    crc: int = 0

    for c in message:
        crc = crc ^ c

        for i in range(8):
            if crc & 0x80 != 0:
                crc = ((crc << 1) & 0xFF) ^ seed
            else:
                crc = (crc << 1) & 0xFF

    return crc & 0xFF
