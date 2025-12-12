from dacite import from_dict
from dataclasses import dataclass, MISSING, fields, field, asdict

from smart_home_server.api.schemaTypes import nameSchema, ipv4Schema, colorSchema, urlSafeSchema, currencyCodeSchema
import smart_home_server.constants as const

from smart_home_server.data_sources.caching import cached
import smart_home_server.data_sources.datasourceFunctions as dsf


class UnknownDatasource(Exception):
    pass

class InvalidDatasource(Exception):
    pass

@dataclass(kw_only=True)
class DatasourceDashboard:
    label: str
    color:str
    enabled: bool = True
    hideable: bool = False

    @staticmethod
    def getSchemaPropertiesRequired():
        return {
            "label": nameSchema,
            "color": colorSchema,
            "enabled": { "type": "boolean" },
            "hideable": { "type": "boolean" }
        }, ["label", "color"]

# allows properties to be read by asdict
# this determines which properties will be sent to frontend
@dataclass
class _Datasource:
    url: str = field(init=False)
    # values: dict[str, list] = field(init=False)
    buttons: list = field(init=False)
    datasourceType: str = field(init=False)

@dataclass(kw_only=True)
class Datasource(_Datasource):
    name:str # used for url and regex, must be unique
    pollingPeriod: int = 60 # should be overriden by subclass, default is here to comply with schema
    dashboard:DatasourceDashboard

    @property
    def url(self) -> str: # pyright: ignore
        return f"api/data/{self.name}"

    @classmethod
    def getSchemaPropertiesRequired(cls):
        props, req = DatasourceDashboard.getSchemaPropertiesRequired()
        return {
            "name": nameSchema,
            "pollingPeriod": { "type": "integer", "minimum": 1, "maximum": 10*60*60 }, # max is just for sanity
            "dashboard": {
                "type": "object",
                "properties": props,
                "required": req,
                'additionalProperties': False,
            },
            "datasourceType": { "const": cls.__qualname__ },
        }, ["name", "dashboard", "datasourceType"]

    @property
    def datasourceType(self) -> str: #pyright: ignore
        return self.__class__.__qualname__

    @property
    def buttons(self) -> list: #pyright: ignore
        return []

    @staticmethod
    def getClass(datasourceType:str) -> type['Datasource']:
        for sc in Datasource.__subclasses__():
            if sc.__qualname__ == datasourceType:
                return sc
        raise UnknownDatasource()

    @staticmethod
    def getSubclasses() -> list[type['Datasource']]:
        res = []
        for sc in Datasource.__subclasses__():
            res.append(sc)
        return res

    @classmethod
    def getDefaults(cls):
        default_values = {}
        for f in fields(cls):
            if f.default is not MISSING:
                default_values[f.name] = f.default
            elif f.default_factory is not MISSING:
                default_values[f.name] = f.default_factory()
        return default_values

    @staticmethod
    def fromJson(j:dict) -> 'Datasource':
        if 'datasourceType' not in j:
            raise UnknownDatasource("Missing datasourceType")
        jcopy = j.copy()

        # remove properties
        for f in fields(_Datasource):
            if f.name in jcopy:
                jcopy.pop(f.name)

        ds = from_dict(Datasource.getClass(j['datasourceType']), jcopy)
        # TODO: this check is redundant given the schema. Also there should be a static method that 
        # each subclasses can implement to validate/sanitize data
        if ds.dashboard.color not in const.colors:
            raise InvalidDatasource(f"{ds.dashboard.color} not in {[k for k in const.colors.keys()]}")

        return ds

    def toJson(self) -> dict:
        return asdict(self)

    @property
    def values(self) -> dict[str, list]: # pyright: ignore
        return {}

    def local(self):
        return {}

    def _value_helper(self, vals:set[str]):
        return {
            f"{self.name}-{val}": ['data', val] for val in vals
        }


@dataclass(kw_only=True)
class DatasourceForex(Datasource):
    src: str
    dest: str
    pollingPeriod:int = 5*60

    @classmethod
    def getSchemaPropertiesRequired(cls):
        baseProp, baseReq = super(DatasourceForex, cls).getSchemaPropertiesRequired()
        baseProp["src"] = currencyCodeSchema
        baseProp["dest"] = currencyCodeSchema
        baseReq.append("src")
        baseReq.append("dest")
        return baseProp, baseReq

    @property
    def values(self):
        return {
            f"{self.name}": ['data', 'rate']
        }

    def local(self):
        return cached(dsf.getForexLocal, self.pollingPeriod//2, src = self.src, dest = self.dest)

@dataclass(kw_only=True)
class DatasourceClock(Datasource):
    pollingPeriod:int = 1

    @property
    def values(self):
        return self._value_helper({'time', 'date', 'day'})

    def local(self):
        return dsf.getClockLocal()

@dataclass(kw_only=True)
class DatasourceAQ(Datasource):
    ip:str
    pollingPeriod:int = 60

    @classmethod
    def getSchemaPropertiesRequired(cls):
        baseProp, baseReq = super(DatasourceAQ, cls).getSchemaPropertiesRequired()
        baseProp["ip"] = ipv4Schema
        baseReq.append("ip")
        return baseProp, baseReq

    @property
    def values(self):
        return self._value_helper({'temp', 'humid', 'pressure', 'iaq', 'co2Eq', 'voc', 'pm1', 'pm2.5', 'pm10', 'co2'})

    def local(self):
        return cached(dsf.getAirQualityServerLocal, self.pollingPeriod//2, ip=self.ip)

@dataclass(kw_only=True)
class DatasourceTempHumid(Datasource):
    ip:str
    pollingPeriod:int = 60

    @classmethod
    def getSchemaPropertiesRequired(cls):
        baseProp, baseReq = super(DatasourceTempHumid, cls).getSchemaPropertiesRequired()
        baseProp["ip"] = ipv4Schema
        baseReq.append("ip")
        return baseProp, baseReq

    @property
    def values(self):
        return self._value_helper({'temp', 'humid', 'pressure'})

    def local(self):
        return cached(dsf.getAirQualityServerLocal, self.pollingPeriod//2, ip=self.ip)

@dataclass(kw_only=True)
class DatasourceWeatherImage(Datasource):
    pollingPeriod:int = 10*60
    locale: str

    @classmethod
    def getSchemaPropertiesRequired(cls):
        baseProp, baseReq = super(DatasourceWeatherImage, cls).getSchemaPropertiesRequired()
        baseProp["locale"] = urlSafeSchema
        baseReq.append("locale")
        return baseProp, baseReq

    @property
    def values(self):
        return {}

    def local(self):
        return cached(dsf.getWeatherImageLocal, self.pollingPeriod//2, locale=self.locale)


@dataclass(kw_only=True)
class DatasourceForcast(Datasource):
    pollingPeriod:int = 10*60
    locale: str

    @classmethod
    def getSchemaPropertiesRequired(cls):
        baseProp, baseReq = super(DatasourceForcast, cls).getSchemaPropertiesRequired()
        baseProp["locale"] = urlSafeSchema
        baseReq.append("locale")
        return baseProp, baseReq

    @property
    def values(self):
        return {
            f'{self.name}-totalPercip': ['data', 'days', 0, 'percip'],
            f'{self.name}-tomorrowTemp': ['data', 'days', 1, 'temp'],
            f'{self.name}-tomorrowPercip': ['data', 'days', 1, 'percip'],
        }

    def local(self):
        return cached(dsf.getForecastLocal, self.pollingPeriod//2, locale = self.locale)

@dataclass(kw_only=True)
class DatasourceWeatherCurrent(Datasource):
    pollingPeriod:int = 10*60
    locale:str

    @classmethod
    def getSchemaPropertiesRequired(cls):
        baseProp, baseReq = super(DatasourceWeatherCurrent, cls).getSchemaPropertiesRequired()
        baseProp["locale"] = urlSafeSchema
        baseReq.append("locale")
        return baseProp, baseReq

    @property
    def values(self):
        return self._value_helper({'text', 'temp', 'humid', "uv", 'percip3h', 'feelsLike', 'sunrise', 'sunset'})

    def local(self):
        return cached(dsf.getCurrentWeather, self.pollingPeriod//2, locale = self.locale)

@dataclass(kw_only=True)
class DatasourceErrors(Datasource):
    pollingPeriod:int = 15

    @property
    def values(self):
        return self._value_helper({'anyErrs'})

    def local(self):
        return dsf.getErrors()

    @property
    def buttons(self):
        return [{
            'text': 'Clear',
            'actions':[
                {'type':'request', 'route':'api/dashboard/errors' , 'method': 'DELETE', 'data':{}},
                {'type': 'reload'},
             ],
        }]
        
@dataclass(kw_only=True)
class DatasourceJobLog(Datasource):
    pollingPeriod:int = 30*60

    def local(self):
        return dsf.getJobLog()

    @property
    def buttons(self):
        return [{
                'text': 'Clear',
                'actions':[
                    {'type':'request', 'route':'api/dashboard/logs' , 'method': 'DELETE', 'data':{'name':'jobLog'}},
                    {'type': 'reload'},
                 ],
            }]

@dataclass(kw_only=True)
class DatasourceRfLog(Datasource):
    pollingPeriod:int = 30*60

    def local(self):
        return dsf.getRfLog()

    @property
    def buttons(self):
        return [{
                'text': 'Clear',
                'actions':[
                    {'type':'request', 'route':'api/dashboard/logs' , 'method': 'DELETE', 'data':{'name':'rfLog'}},
                    {'type': 'reload'},
                 ],
            }]

@dataclass(kw_only=True)
class DatasourceVersion(Datasource):
    pollingPeriod:int = 10*60

    def local(self):
        return dsf.getServerVersion()

    @property
    def values(self):
        return self._value_helper({'version'})

