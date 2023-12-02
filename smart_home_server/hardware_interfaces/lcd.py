from smart_home_server.errors import currentErrors 

import smart_home_server.constants as const

# Generally 27 is the address;Find yours using: i2cdetect -y 1

_lastWritten = const.lcdLines * [""]

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
                _lastWritten[i] = lines[i]

        if same:
            return

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



# used to get current format for dashboard
_fmt = ""

class IgnoreMissingDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

spaceFormat = "space"
noSpace = IgnoreMissingDict({spaceFormat:""})
oneSpace = IgnoreMissingDict({spaceFormat:" "})
def fillSpacesAndClamp(lines):
    res = []
    for i in range(min(len(lines), const.lcdLines)):
        line = lines[i]
        size = len(line.format_map(noSpace))
        numSpaces = len(line.format_map(oneSpace)) - size
        spaceSize = 0 if numSpaces < 1 else (const.lcdWidth - size)//numSpaces
        line = line.format_map(IgnoreMissingDict({spaceFormat:" "*spaceSize}))

        # clamp length
        line = line if len(line) <= const.lcdWidth else line[0:const.lcdWidth]
        res.append(line)

    return res

def printfLCD(replacements):
    global _fmt
    try:
        text = _fmt.format_map(IgnoreMissingDict(replacements))
        lines = text.split('\n')
        lines = fillSpacesAndClamp(lines)
    except Exception as e:
        print(f"LCD Format Error: \n{e}")
        currentErrors['Conseq_LCD_Write_Err'] += 1 
        return

    try:
        writeLCD(lines)
    except Exception as e:
        print(f"LCD Write Error: \n{e}")
        currentErrors['Conseq_LCD_Write_Err'] += 1 
        return
    currentErrors['Conseq_LCD_Write_Err'] = 0

def getLCDFMT():
    global _fmt
    return _fmt

def setLCDFMT(fmt):
    global _fmt
    _fmt = fmt

