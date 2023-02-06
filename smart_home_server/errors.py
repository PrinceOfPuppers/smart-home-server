currentErrors = {
    'Conseq_DHT_Read_Err': 0,     # consequtive
    'Conseq_LCD_Write_Err': 0,    # consequtive
    'Conseq_Scheduler_Err': 0,    # consequtive
    'Last_Job_Run_Err': '',
    'Misc_Errs': [],              # for testing
}

def getErrorStrAndBool():
    # returns error string and bool indicating if there are any errors
    s = ""

    if currentErrors['Conseq_DHT_Read_Err'] > 0:
        s += f'DHT Read Err Chain: {currentErrors["Conseq_DHT_Read_Err"]}\n'
    if currentErrors['Conseq_LCD_Write_Err'] > 0:
        s += f'LCD Write Err Chain: {currentErrors["Conseq_LCD_Write_Err"]}\n'
    if currentErrors['Conseq_Scheduler_Err'] > 0:
        s += f'Scheduler Err Chain: {currentErrors["Conseq_Scheduler_Err"]}\n'
    if currentErrors['Last_Job_Run_Err']:
        s += f"{currentErrors['Last_Job_Run_Err']}\n"
    for err in currentErrors['Misc_Errs']:
        s += f"{err}\n"

    if not s:
        return 'No Errors', False
    return s, True
