currentErrors = {
    # consequtive
    'Conseq_DHT_Read_Err': 0,
    'Conseq_BME_Read_Err': 0,
    'Conseq_Weather_Server_Read_Err': 0,
    'Conseq_LCD_Write_Err': 0,
    'Conseq_Scheduler_Err': 0,

    'Last_Job_Run_Err': '',
    'Misc_Errs': [],              # for testing
    'Subscribe_Manager_None': set(),  # for when a datasource returns none in subscribe manager
    'Dashboard_None': set()          # for when a datasource returns none on the dashboard
}

def getErrorStrAndBool():
    # returns error string and bool indicating if there are any errors
    s = ""

    if currentErrors['Conseq_DHT_Read_Err'] > 0:
        s += f'DHT Read Err Chain: {currentErrors["Conseq_DHT_Read_Err"]}\n'
    if currentErrors['Conseq_BME_Read_Err'] > 0:
        s += f'BME Read Err Chain: {currentErrors["Conseq_BME_Read_Err"]}\n'
    if currentErrors['Conseq_Weather_Server_Read_Err'] > 0:
        s += f'Weather Server Err Chain: {currentErrors["Conseq_Weather_Server_Read_Err"]}\n'
    if currentErrors['Conseq_LCD_Write_Err'] > 0:
        s += f'LCD Write Err Chain: {currentErrors["Conseq_LCD_Write_Err"]}\n'
    if currentErrors['Conseq_Scheduler_Err'] > 0:
        s += f'Scheduler Err Chain: {currentErrors["Conseq_Scheduler_Err"]}\n'

    if currentErrors['Last_Job_Run_Err']:
        s += f"{currentErrors['Last_Job_Run_Err']}\n"
    for err in currentErrors['Misc_Errs']:
        s += f"{err}\n"

    for name in currentErrors['Subscribe_Manager_None']:
        s += f"Sub Source Err: {name}\n"

    for name in currentErrors['Dashboard_None']:
        s += f"Dash Source Err: {name}\n"

    if not s:
        return 'No Errors', False
    return s, True
