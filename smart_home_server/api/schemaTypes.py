import smart_home_server.constants as const

nameSchema = {"type": "string", "minLength": 0, "maxLength": 20, "pattern": "^[^\n\r]*$"}
urlSafeSchema = {"type": "string", "minLength": 1, "maxLength": 100, "pattern": "^[A-Za-z0-9,]+$"}
idSchema = {"type": "string", "minLength": 0, "maxLength": 50, "pattern": "^[^\n\r]*$"}
colorSchema = {"enum": [color for color in const.colors.keys()]}
ipv4Schema = {"type": "string", "minLength": 1, "maxLength": 15, 
              "pattern": r"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$"}
currencyCodeSchema = {"type": "string", "minLength": 0, "maxLength": 3, "pattern": "^[A-Z]{3}$"}
