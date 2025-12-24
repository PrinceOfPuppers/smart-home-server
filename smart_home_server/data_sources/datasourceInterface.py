import smart_home_server.data_sources.datasourceTypes as dst
import smart_home_server.constants as const
from threading import Lock
from copy import copy
import os
import json
from typing import Union

class DatasourceFileCorrupted(Exception):
    pass

dsFileLock = Lock()

def _getDatasourcePath():
    return f"{const.datasourcesFolder}/datasources.json"

class DatasourceStorage:
    def __init__(self):
        self.datasourceDict: dict = dict()
        self.datasourceOrder: list[str] = list()
        self._datavalues: dict | None = None
        self._datasourceList: list | None = None

        with dsFileLock:
            path = _getDatasourcePath()

            # ensure file exists
            if not os.path.exists(path):
                # create blank file
                with open(path, "w") as f:
                    json.dump({'order': [], 'datasources': {}}, f)

            with open(path, "r") as f:
                try:
                    j = json.loads(f.read())
                except Exception as e:
                    raise DatasourceFileCorrupted("Unable Decode Datasource json") from e
                if not isinstance(j, dict) or 'order' not in j or 'datasources' not in j:
                    raise DatasourceFileCorrupted("Datasource json format incorrect")

            self.datasourceOrder = j['order']
            for name, datasourceRaw in j['datasources'].items():
                if name != datasourceRaw['name']:
                    raise DatasourceFileCorrupted("Datasource name does not match")

                source = dst.Datasource.fromjson(datasourceRaw)

                self.datasourceDict[source.name] = source


    def getSources(self, valueKeys: list) -> list:
        res = []

        for key in valueKeys:
            if key not in self.datavalues:
                continue
            res.append(self.datasourceDict[self.datavalues[key]])

        return res

    def getSourceDict(self, valueKeys: set|list) -> dict:
        res = {}
        for key in valueKeys:
            if key not in self.datavalues:
                continue
            res[self.datavalues[key]] = self.datasourceDict[self.datavalues[key]]

        return res

    # gets polling period of the source that yeilds provided value
    def getPollingPeriod(self, valueKey:str) -> Union[int, None]:
        for source in self.datasourceList:
            if not valueKey in source.values:
                continue
            return source.pollingPeriod
        return None


    @property
    def datavalues(self):
        if self._datavalues == None:
            self._datavalues  = dict()
            for source in self.datasourceDict.values():
                for key in source.values.keys():
                    self._datavalues[key] = source.name
        return self._datavalues

    @property
    def datasourceList(self):
        if self._datasourceList == None:
            self._datasourceList = []
            for name in self.datasourceOrder:
                self._datasourceList.append(self.datasourceDict[name])
        return self._datasourceList


# only one instance can exist (caches file state)
class DatasourceStorageMutable(DatasourceStorage):
    def __init__(self):
        super().__init__()
        self.dsMutableLock:Lock = Lock()


    def _assertOrderOverlap(self, datasources, order):
        if set(order) != datasources.keys():
            raise dst.UnknownDatasource(f"Datasources order and DatasourcesDict keys are not Identical: \norder: {order} \nkeys: {[k for k in datasources.keys()]}")

    def writeback(self):
        with dsFileLock:
            path = _getDatasourcePath()

            datasources = {k: d.toJson() for k, d in self.datasourceDict.items()}
            order = self.datasourceOrder
            self._assertOrderOverlap(datasources, order)

            with open(path, "w") as f:
                json.dump({'order': order, 'datasources': datasources}, f)


    def editDatasource(self, oldName, datasource):
        with self.dsMutableLock:
            if not isinstance(datasource, dst.Datasource):
                raise ValueError("datasource argument is not Datasource")

            orderIndex = self.datasourceOrder.index(oldName)

            if oldName not in self.datasourceDict or orderIndex < 0:
                raise dst.UnknownDatasource(f"Unknown Datasource: {oldName}\nCurrentSources: {[k for k in self.datasourceDict.keys()]} \nOrder:{self.datasourceOrder}")

            self._datavalues = None
            self._datasourceList = None

            del self.datasourceDict[oldName]
            self.datasourceDict[datasource.name] = copy(datasource)
            self.datasourceOrder[orderIndex] = datasource.name

            self.writeback()

    def deleteDatasource(self, name):
        with self.dsMutableLock:
            self._datavalues = None
            self._datasourceList = None

            orderIndex = self.datasourceOrder.index(name)
            if orderIndex >= 0:
                del self.datasourceOrder[orderIndex]

            if name in self.datasourceDict:
                del self.datasourceDict[name]

            self.writeback()

    def editDatasoruceOrder(self, newOrder):
        with self.dsMutableLock:
            self._assertOrderOverlap(self.datasourceDict, newOrder)

            self._datasourceList = None
            self.datasourceOrder = newOrder.copy()
            self.writeback()

    def appendDatasource(self, datasource):
        with self.dsMutableLock:
            if not isinstance(datasource, dst.Datasource):
                raise ValueError("datasource argument is not Datasource")
            if datasource.name in self.datasourceDict:
                raise dst.DatasourceAlreadyExists(f"Datasource Named {datasource.name} Already Exists")

            self._datavalues = None
            self._datasourceList = None
            self.datasourceDict[datasource.name] = copy(datasource)
            self.datasourceOrder.append(datasource.name)
            self.writeback()

    @property
    def datavalues(self):
        with self.dsMutableLock:
            return super().datavalues

    @property
    def datasourceList(self):
        with self.dsMutableLock:
            return super().datasourceList


# immutable at runtime
datasources = DatasourceStorage()

# edited by frontend, changes aren't loaded into immutable until restart
datasourcesMutable = DatasourceStorageMutable()

