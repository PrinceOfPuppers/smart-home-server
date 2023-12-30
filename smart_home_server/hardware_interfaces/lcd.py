import smart_home_server.constants as const

# Generally 27 is the address;Find yours using: i2cdetect -y 1

_lastWritten = [""]

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

    def writeLCD(lines):
        global _lcd
        global _lastWritten
        if _lcd is None:
            startLCD()

        assert _lcd is not None

        same = True

        if len(lines) != len(_lastWritten):
            same = False
        else:
            for i in range(len(_lastWritten)):
                if lines[i] != _lastWritten[i]:
                    same=False
                    break

        if same:
            return

        _lastWritten = lines.copy()
        _lcd.clear()
        for line in lines:
            _lcd.write_string(line)
            _lcd.crlf()

    def toggleBacklight():
        global _lcd
        if _lcd is None:
            startLCD()
        assert _lcd is not None
        _lcd.backlight_enabled = not _lcd.backlight_enabled

    def setBacklight(on:bool):
        global _lcd
        if _lcd is None:
            startLCD()
        _lcd.backlight_enabled = on

else:
    def startLCD():
        pass
    def stopLCD():
        pass
    def clearLCD():
        pass
    def writeLCD(lines):
        s = '\n'.join(lines)
        print(f"Write LCD:\n{s}\n", flush=True)

    def toggleBacklight():
        print("LCD Backlight Toggled\n", flush=True)
        pass

    def setBacklight(on:bool):
        print(f"LCD Backlight Set: {'on' if on else 'off'}\n", flush=True)



