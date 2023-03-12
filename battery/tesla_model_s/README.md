# Tesla Model S Modules

These modules are high quality and come with a BMS board that is able to balance the cells. The BMS Board uses a [bq76PL536A battery management chip](https://www.ti.com/product/BQ76PL536A) from TI.

## Communication

The modules are connected in a daisy-chained bus. They use 5V TTL level serial communications running at 612500 baud. Addresses range from 0x01 to 0x3E, with 0x3F as the broadcast address. As one module receives a message, if it is the intended recipient it will reply and forward on the response up the chain of devices. As it is passed on to the other modules in the chain, they will ignore it and pass it on, eventually returning back to the sender. Any communications to address zero will have their address modified to 0x80 before passing up the chain of devices so that other devices don't match

The modules implement a simple register based protocol.

### Request

| Byte   | Content                                              |
| ------ | ---------------------------------------------------- |
| Byte 0 | Bit 0 = read (0) / write (1), Bits 1 - 6 = Address   |
| Byte 1 | Register address                                     |
| Byte 2 | Read: number of bytes to read. Write: Value to write |
| Byte 3 | Checksum                                             |

### Response

For a read response:

| Byte      | Content          |
| --------- | ---------------- |
| Byte 0    | Address          |
| Byte 1    | Register address |
| Byte 2    | Data length      |
| Byte n    | Register data    |
| Last Byte | Checksum         |

For a write response:

| Byte   | Content          |
| ------ | ---------------- |
| Byte 0 | Address          |
| Byte 1 | Register address |
| Byte 2 | Register value   |
| Byte 3 | Checksum         |

For details on the register locations, see the table in the datasheet.
