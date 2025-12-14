import smart_home_server.data_sources.datasourceTypes as dst
import smart_home_server.constants as const
import os
import json
from typing import Union

class DatasourceFileCorrupted(Exception):
    pass


# dataValue: datasourceName
datavalues:dict[str, str] = {}
datasourceList:list = []
datasourceDict:dict = {}

def _getDatasourcePath():
    return f"{const.datasourcesFolder}/datasources.json"

def loadDatasources():
    # normalize state
    datasourceList.clear()
    datavalues.clear()
    datasourceDict.clear()

    path = _getDatasourcePath()
    # ensure file exists
    if not os.path.exists(path):
        # create blank file, clear lists
        with open(path, "w") as f:
            f.write(json.dumps([]))
            
    with open(path, "r") as f:
        try:
            j = json.loads(f.read())
        except Exception as e:
            raise DatasourceFileCorrupted("Unable Decode Datasource json") from e
        if not isinstance(j, list):
            raise DatasourceFileCorrupted("Datasource json is not List")
        tmp = []
        for datasourceRaw in j:
            source = dst.Datasource.fromJson(datasourceRaw)
            tmp.append(source)
            datasourceDict[source.name] = source
            for key in source.values.keys():
                datavalues[key] = source.name


def saveDatasources(datasourceJson:list[dict]):
    # ensure data can be converted to datasources before saving
    _ = [dst.Datasource.fromJson(x) for x in datasourceJson] 

    path = _getDatasourcePath()
    with open(path, "w") as f:
        f.write(json.dumps(datasourceJson))

def getSources(valueKeys: list) -> list:
    res = []

    for key in valueKeys:
        if key not in datavalues:
            continue
        res.append(datasourceDict[datavalues[key]])

    return res

def getSourceDict(valueKeys: set|list) -> dict:
    res = {}
    for key in valueKeys:
        if key not in datavalues:
            continue
        res[datavalues[key]] = datasourceDict[datavalues[key]]

    return res

# gets polling period of the source that yeilds provided value
def getPollingPeriod(valueKey:str) -> Union[int, None]:
    for source in datasourceList:
        if not valueKey in source.values:
            continue
        return source.pollingPeriod
    return None

# sources are only loaded on stack launch.
# for saves to take effect, stack must be relaunched
loadDatasources()

