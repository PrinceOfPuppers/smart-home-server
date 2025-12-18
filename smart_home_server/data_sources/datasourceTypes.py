from dataclasses import dataclass, field
from typing import Annotated

from smart_home_server.api.schemaTypes import nameConstraints, ipv4Constraints, colorConstraints, urlSafeConstraints, currencyConstraints
import smart_home_server.annotations as ann
from functools import cache 

from smart_home_server.data_sources.caching import cached
import smart_home_server.data_sources.datasourceFunctions as dsf


class UnknownDatasource(Exception):
    pass

class InvalidDatasource(Exception):
    pass

class DatasourceAlreadyExists(Exception):
    pass


pollingPeriodAnnotation = Annotated[int, ann.IntConstraints(minimum=1, maximum=10*60*60), ann.UiInfo(label="Polling Sec", labelCaps=False)]

@dataclass(kw_only=True)
class DatasourceDashboard:
    label: Annotated[str, nameConstraints]
    color: Annotated[str, colorConstraints, ann.UiInfo(br=False)]
    enabled: Annotated[bool, ann.BoolConstraints(), ann.UiInfo(br=False)] = True
    hideable: Annotated[bool, ann.BoolConstraints()] = False


# allows properties to be read by asdict
# this determines which properties will be sent to frontend
@dataclass(frozen=True)
class _Datasource:
    url: str = field(init=False)
    # values: dict[str, list] = field(init=False)
    buttons: list = field(init=False)

@dataclass(kw_only=True, frozen=True)
class Datasource(_Datasource):
    datasourceType:Annotated[
        str,
        ann.ConstConstraints(),
        ann.UiInfo(label="Type")
    ] = field(init=False)

    name: Annotated[str, nameConstraints, ann.UiInfo(size=10, br=False)] # used for url and regex, must be unique
    pollingPeriod: pollingPeriodAnnotation = 60 # should be overriden by subclass, default is here to comply with schema
    dashboard:Annotated[DatasourceDashboard, ann.ObjectConstraints()]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ann.ConstConstraints.create_discriminator(cls, "datasourceType")

    # override this method to sanitize data or throw exception
    @staticmethod
    def sanitize(data: dict):
        return data

    @staticmethod
    def fromjson(j:dict) -> 'Datasource':
        return ann.from_json(Datasource, j, "datasourceType", lambda dclass, data: dclass.sanitize(data))

    def toJson(self) -> dict:
        return ann.to_json(self)

    @classmethod
    def getSchema(cls):
        return ann.json_schema_from_dataclass(cls)

    # returns dict {datasourceType: schema}
    @classmethod
    @cache
    def getSchemaTypeDict(cls):
        
        x = cls.getSchema()
        assert x is not None
        datasourceSchemas = x['oneOf']
        assert isinstance(datasourceSchemas, list)

        res = {}
        for schema in datasourceSchemas:
            dsType = schema["properties"]["datasourceType"]["const"]
            res[dsType] = schema
        return res

    @property
    def url(self) -> str: # pyright: ignore
        return f"/api/data/{self.name}"

    @property
    def buttons(self) -> list: #pyright: ignore
        return []

    @property
    def values(self) -> dict[str, list]: # pyright: ignore
        return {}

    def local(self):
        return {}

    def _value_helper(self, vals:set[str]):
        return {
            f"{self.name}-{val}": ['data', val] for val in vals
        }


@dataclass(kw_only=True, frozen=True)
class DatasourceForex(Datasource):
    src: Annotated[str, currencyConstraints, ann.UiInfo(br=False)]
    dest: Annotated[str, currencyConstraints]
    pollingPeriod:pollingPeriodAnnotation = 5*60

    @property
    def values(self):
        return {
            f"{self.name}": ['data', 'rate']
        }

    @staticmethod
    def sanitize(data: dict):
        data['src'] = data['src'].upper()
        data['dest'] = data['dest'].upper()
        return data

    def local(self):
        return cached(dsf.getForexLocal, self.pollingPeriod//2, src = self.src, dest = self.dest)

@dataclass(kw_only=True, frozen=True)
class DatasourceClock(Datasource):
    pollingPeriod:pollingPeriodAnnotation = 1

    @property
    def values(self):
        return self._value_helper({'time', 'date', 'day'})

    def local(self):
        return dsf.getClockLocal()

@dataclass(kw_only=True, frozen=True)
class DatasourceAQ(Datasource):
    ip: Annotated[str, ipv4Constraints]
    pollingPeriod: pollingPeriodAnnotation = 60

    @property
    def values(self):
        return self._value_helper({'temp', 'humid', 'pressure', 'iaq', 'co2Eq', 'voc', 'pm1', 'pm2.5', 'pm10', 'co2'})

    def local(self):
        return cached(dsf.getAirQualityServerLocal, self.pollingPeriod//2, ip=self.ip)

@dataclass(kw_only=True, frozen=True)
class DatasourceTempHumid(Datasource):
    ip: Annotated[str, ipv4Constraints]
    pollingPeriod: pollingPeriodAnnotation = 60

    @property
    def values(self):
        return self._value_helper({'temp', 'humid', 'pressure'})

    def local(self):
        return cached(dsf.getAirQualityServerLocal, self.pollingPeriod//2, ip=self.ip)

@dataclass(kw_only=True, frozen=True)
class DatasourceWeatherImage(Datasource):
    pollingPeriod:pollingPeriodAnnotation = 10*60
    locale: Annotated[str, urlSafeConstraints]

    @property
    def values(self):
        return {}

    def local(self):
        return cached(dsf.getWeatherImageLocal, self.pollingPeriod//2, locale=self.locale)


@dataclass(kw_only=True, frozen=True)
class DatasourceForcast(Datasource):
    pollingPeriod:pollingPeriodAnnotation = 10*60
    locale: Annotated[str, urlSafeConstraints]

    @property
    def values(self):
        return {
            f'{self.name}-totalPercip': ['data', 'days', 0, 'percip'],
            f'{self.name}-tomorrowTemp': ['data', 'days', 1, 'temp'],
            f'{self.name}-tomorrowPercip': ['data', 'days', 1, 'percip'],
        }

    def local(self):
        return cached(dsf.getForecastLocal, self.pollingPeriod//2, locale = self.locale)

@dataclass(kw_only=True, frozen=True)
class DatasourceWeatherCurrent(Datasource):
    pollingPeriod:pollingPeriodAnnotation = 10*60
    locale: Annotated[str, urlSafeConstraints]

    @property
    def values(self):
        return self._value_helper({'text', 'temp', 'humid', "uv", 'percip3h', 'feelsLike', 'sunrise', 'sunset'})

    def local(self):
        return cached(dsf.getCurrentWeather, self.pollingPeriod//2, locale = self.locale)

@dataclass(kw_only=True, frozen=True)
class DatasourceErrors(Datasource):
    pollingPeriod:pollingPeriodAnnotation = 15

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
        
@dataclass(kw_only=True, frozen=True)
class DatasourceJobLog(Datasource):
    pollingPeriod:pollingPeriodAnnotation = 30*60

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

@dataclass(kw_only=True, frozen=True)
class DatasourceRfLog(Datasource):
    pollingPeriod:pollingPeriodAnnotation = 30*60

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

@dataclass(kw_only=True, frozen=True)
class DatasourceVersion(Datasource):
    pollingPeriod:pollingPeriodAnnotation = 10*60

    def local(self):
        return dsf.getServerVersion()

    @property
    def values(self):
        return self._value_helper({'version'})

