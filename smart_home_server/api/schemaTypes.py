import smart_home_server.constants as const
import smart_home_server.annotations as ann
import inspect

# TODO: remove *Schema once port is finished

nameSchema = {"type": "string", "minLength": 0, "maxLength": 20, "pattern": "^[^\n\r]*$"}
nameConstraints = ann.StrConstraints(**{k:nameSchema[k] for k in inspect.signature(ann.StrConstraints).parameters})

urlSafeSchema = {"type": "string", "minLength": 1, "maxLength": 100, "pattern": "^[A-Za-z0-9,]+$"}
urlSafeConstraints = ann.StrConstraints(**{k:urlSafeSchema[k] for k in inspect.signature(ann.StrConstraints).parameters})

idSchema = {"type": "string", "minLength": 0, "maxLength": 50, "pattern": "^[^\n\r]*$"}
idConstraints = ann.StrConstraints(**{k:idSchema[k] for k in inspect.signature(ann.StrConstraints).parameters})

colorSchema = {"enum": [color for color in const.colors.keys()]}
colorConstraints = ann.EnumConstraints(values = {color for color in const.colors.keys()})

ipv4Schema = {"type": "string", "minLength": 1, "maxLength": 15, "pattern": r"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$"}
ipv4Constraints = ann.StrConstraints(**{k:ipv4Schema[k] for k in inspect.signature(ann.StrConstraints).parameters})

currencyCodeSchema = {"type": "string", "minLength": 0, "maxLength": 3, "pattern": "^[A-Z]{3}$"}
currencyConstraints = ann.StrConstraints(**{k:currencyCodeSchema[k] for k in inspect.signature(ann.StrConstraints).parameters})
