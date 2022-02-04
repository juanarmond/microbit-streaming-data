radio.set_group(1)
radio.set_transmit_power(7)
radio.set_transmit_serial_number(True)
serial.set_baud_rate(BaudRate.BAUD_RATE115200)
basic.show_icon(IconNames.SAD)

radio.on_received_value(on_received_value)


def on_received_value(name, value):
    serial.write_string("{")
    basic.show_leds(
        """
        . . . . .
                . . . . .
                . . . . .
                . . . . .
                . . . . .
    """
    )
    serial.write_string(
        '"time":' + str(radio.received_packet(RadioPacketProperty.TIME)) + ","
    )
    basic.show_leds(
        """
        # . . . .
                # . . . .
                # . . . .
                # . . . .
                # . . . .
    """
    )
    serial.write_string(
        '"serial":'
        + str(radio.received_packet(RadioPacketProperty.SERIAL_NUMBER))
        + ","
    )
    basic.show_leds(
        """
        # # . . .
                # # . . .
                # # . . .
                # # . . .
                # # . . .
    """
    )
    serial.write_string(
        '"signal":'
        + str(radio.received_packet(RadioPacketProperty.SIGNAL_STRENGTH))
        + ","
    )
    basic.show_leds(
        """
        # # # . .
                # # # . .
                # # # . .
                # # # . .
                # # # . .
    """
    )
    serial.write_string('"key":"' + name + '",')
    basic.show_leds(
        """
        # # # # .
                # # # # .
                # # # # .
                # # # # .
                # # # # .
    """
    )
    serial.write_string('"value":' + str(value))
    serial.write_line("}")
    basic.show_leds(
        """
        # # # # #
                # # # # #
                # # # # #
                # # # # #
                # # # # #
    """
    )
