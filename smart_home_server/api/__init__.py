import smart_home_server.constants as const

remotePressSchema = \
{
    "type": "object",
    "properties": {
        "channel": { "type": "integer", "minimum": 0, "maximum": len(const.txChannels)-1}, # defaults to 0
        "value": { "type": "boolean" } # defaults to True
    },
    'additionalProperties': False,
}
