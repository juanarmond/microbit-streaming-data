speed = 0
sensor = 0
counter = 0
i = 0
list3: List[number] = []
list2: List[number] = []
list1: List[str] = []
moveMotorZIP: Kitronik_Move_Motor.MoveMotorZIP = None
radio.set_group(1)
radio.set_transmit_power(7)
radio.set_transmit_serial_number(True)
basic.show_icon(IconNames.HAPPY)
soundExpression.twinkle.play()
moveMotorZIP = Kitronik_Move_Motor.create_move_motor_zipled(4)
list1 = [
    "a.x",
    "a.y",
    "a.z",
    "tembo",
    "temp",
    "sensor",
    "light",
    "compass",
    "sound",
    "mag.x",
    "mag.y",
    "mag.z",
    "mag.str",
    "left",
    "right",
    "millivolts",
]
list2 = [
    input.acceleration(Dimension.X),
    input.acceleration(Dimension.Y),
    input.acceleration(Dimension.Z),
    music.tempo(),
    input.temperature(),
    Kitronik_Move_Motor.measure(),
    input.light_level(),
    input.compass_heading(),
    input.sound_level(),
    input.magnetic_force(Dimension.X),
    input.magnetic_force(Dimension.Y),
    input.magnetic_force(Dimension.Z),
    input.magnetic_force(Dimension.STRENGTH),
    Kitronik_Move_Motor.read_sensor(Kitronik_Move_Motor.LfSensor.LEFT),
    Kitronik_Move_Motor.read_sensor(Kitronik_Move_Motor.LfSensor.RIGHT),
    pins.analog_read_pin(AnalogPin.P0) * (1000 / 340),
]
Kitronik_Move_Motor.set_ultrasonic_units(Kitronik_Move_Motor.Units.CENTIMETERS)
Kitronik_Move_Motor.turn_radius(Kitronik_Move_Motor.TurnRadii.TIGHT)
radio.send_value("carSN", control.device_serial_number())


def transmitAllValues():
    global list3, i, counter
    moveCar()
    list3 = [
        input.acceleration(Dimension.X),
        input.acceleration(Dimension.Y),
        input.acceleration(Dimension.Z),
        music.tempo(),
        input.temperature(),
        Kitronik_Move_Motor.measure(),
        input.light_level(),
        input.compass_heading(),
        input.sound_level(),
        input.magnetic_force(Dimension.X),
        input.magnetic_force(Dimension.Y),
        input.magnetic_force(Dimension.Z),
        input.magnetic_force(Dimension.STRENGTH),
        Kitronik_Move_Motor.read_sensor(Kitronik_Move_Motor.LfSensor.LEFT),
        Kitronik_Move_Motor.read_sensor(Kitronik_Move_Motor.LfSensor.RIGHT),
        pins.analog_read_pin(AnalogPin.P0) * (1000 / 340),
    ]
    i = 0
    for elem in list3:
        moveCar()
        tmp = elem
        basic.show_leds(
            """
            . . . . .
                        . . . . .
                        . . . . .
                        . . . . .
                        . . . . .
        """
        )
        # radio.send_value(str(list2[i]), tmp)
        # radio.send_value(str(list3[i]), tmp)
        if list2[i] == tmp or counter == 0:
            moveCar()
            basic.show_leds(
                """
                # . . . .
                                # . . . .
                                # . . . .
                                # . . . .
                                # . . . .
            """
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
            basic.show_leds(
                """
                # # # . .
                                # # # . .
                                # # # . .
                                # # # . .
                                # # # . .
            """
            )
            basic.show_leds(
                """
                # # # # .
                                # # # # .
                                # # # # .
                                # # # # .
                                # # # # .
            """
            )
            list2[i] = tmp
            radio.send_value(list1[i], tmp)
            basic.show_leds(
                """
                # # # # #
                                # # # # #
                                # # # # #
                                # # # # #
                                # # # # #
            """
            )
            moveCar()
            basic.pause(1000)
        i += 1
    counter += 1
    radio.send_value("seconds", input.running_time() / 1000 % 60)
    moveCar()
    basic.pause(5000)


def moveCar():
    global sensor, speed
    Kitronik_Move_Motor.motor_balance(Kitronik_Move_Motor.SpinDirections.LEFT, 0)
    sensor = Kitronik_Move_Motor.measure()
    speed = 30
    if sensor > 15 and sensor < 20:
        Kitronik_Move_Motor.beep_horn()
        moveMotorZIP.show_color(
            Kitronik_Move_Motor.colors(Kitronik_Move_Motor.ZipLedColors.YELLOW)
        )
        Kitronik_Move_Motor.move(Kitronik_Move_Motor.DriveDirections.RIGHT, speed)
    elif sensor <= 15:
        Kitronik_Move_Motor.spin(Kitronik_Move_Motor.SpinDirections.RIGHT, speed)
        moveMotorZIP.show_color(
            Kitronik_Move_Motor.colors(Kitronik_Move_Motor.ZipLedColors.RED)
        )
    else:
        Kitronik_Move_Motor.move(Kitronik_Move_Motor.DriveDirections.FORWARD, speed)
        moveMotorZIP.show_color(
            Kitronik_Move_Motor.colors(Kitronik_Move_Motor.ZipLedColors.BLUE)
        )


def on_forever():
    moveCar()
    transmitAllValues()


basic.forever(on_forever)
