import smart_home_server.constants as const

# Generally 27 is the address;Find yours using: i2cdetect -y 1

if const.isRpi():
    _lcd = None
    from RPLCD import i2c
    def startLCD():
        global _lcd

        if _lcd is not None:
            return

        port = 1 # 0 on an older Raspberry Pi
        charmap = 'A00'
        i2c_expander = 'PCF8574'
        _lcd = i2c.CharLCD(i2c_expander, const.lcdI2CAddress, port=port, charmap=charmap,
                          cols=const.lcdWidth, rows=const.lcdLines)
    def stopLCD():
        global _lcd
        if _lcd is not None:
            _lcd.close(clear=True)
        _lcd = None

    def clearLCD():
        global _lcd
        if _lcd is None:
            startLCD()
        assert _lcd is not None
        _lcd.crlf()

    def writeLCD(s):
        global _lcd
        if _lcd is None:
            startLCD()
        assert _lcd is not None
        _lcd.crlf()
        _lcd.write_string(s)

    def toggleBacklight():
        global _lcd
        if _lcd is None:
            startLCD()
        assert _lcd is not None
        _lcd.backlight_enabled = not _lcd.backlight_enabled
else:
    def startLCD():
        pass
    def stopLCD():
        pass
    def clearLCD():
        pass
    def writeLCD(s):
        print(f"Write LCD:\n{s}\n", flush=True)

    def toggleBacklight():
        print("LCD Backlight Toggled\n", flush=True)
        pass

