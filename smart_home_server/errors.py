currentErrors = {
    'Conseq_DHT_Read_Err': 0,     # consequtive
    'Conseq_LCD_Write_Err': 0,    # consequtive
}

def appendConequtiveErr(s, repr, key):
    if currentErrors[key] > 0:
        s += repr + f' Chain: {currentErrors[key]}'

def getErrorStrAndBool():
    # returns error string and bool indicating if there are any errors
    s = ""

    if currentErrors['Conseq_DHT_Read_Err'] > 0:
        s += f'DHT Read Err Chain: {currentErrors["Conseq_DHT_Read_Err"]}'
    if currentErrors['Conseq_LCD_Write_Err'] > 0:
        s += f'LCD Write Err Chain: {currentErrors["Conseq_LCD_Write_Err"]}'

    if not s:
        return 'No Errors', False
    return s, True
