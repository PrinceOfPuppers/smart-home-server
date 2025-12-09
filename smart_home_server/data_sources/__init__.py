import smart_home_server.data_sources.datasources as ds
import smart_home_server.constants as const
import os
import json
from typing import Union

class DatasourceFileCorrupted(Exception):
    pass


datavalues = set()
datasourceList:list[ds.Datasource] = []
datasourceDict:dict[str, ds.Datasource] = {}

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
            source = ds.Datasource.fromJson(datasourceRaw)
            tmp.append(source)
            datasourceDict[source.name] = source
            datavalues.add(source.values.keys())


def saveDatasources(datasourceJson:list[dict]):
    # ensure data can be converted to datasources before saving
    _ = [ds.Datasource.fromJson(x) for x in datasourceJson] 

    path = _getDatasourcePath()
    with open(path, "w") as f:
        f.write(json.dumps(datasourceJson))

def getSources(valueKeys: list) -> list[ds.Datasource]:
    res = []

    for source in datasourceList:
        for key in valueKeys:
            if key in source.values:
                res.append(source)
                break
    return res

def getSourceDict(valueKeys: set) -> dict[str, ds.Datasource]:
    res = {}

    for name, source in datasourceDict.items():
        for key in source.values:
            if key in valueKeys:
                res[name] = source
                break
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

