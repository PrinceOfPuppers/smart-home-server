currentErrors = {
    'Conseq_DHT_Read_Err': 0, # consequtive
}

def getErrorStrAndBool():
    # returns error string and bool indicating if there are any errors
    s = ""

    if currentErrors['Conseq_DHT_Read_Err'] > 0:
        s += f"DHT Read Err Chain: {currentErrors['Conseq_DHT_Read_Err']}"

    if not s:
        return 'No Errors', False
    return s, True
