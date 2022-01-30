from tabulate import tabulate
import readline
import re
import os
from functools import reduce
from Types import DataTypeByNum
from Types import ParameterException, ConnectException
from time import time


def getPackageVersion():
    import pkg_resources  # part of setuptools

    try:
        version = pkg_resources.require("milvus_cli")[0].version
    except Exception as e:
        raise ParameterException(
            "Could not get version under single executable file mode."
        )
    return version


def checkEmpty(x):
    return not not x


def getMilvusTimestamp(isSimilar=True):
    ts = time()
    if isSimilar:
        return int(ts) << 18


class PyOrm(object):
    host = "127.0.0.1"
    port = 19530
    alias = "default"

    def connect(self, alias=None, host=None, port=None, disconnect=False):
        self.alias = alias
        self.host = host
        self.port = port
        from pymilvus import connections

        if disconnect:
            connections.disconnect(alias)
            return
        connections.connect(self.alias, host=self.host, port=self.port)

    def checkConnection(self):
        from pymilvus import list_collections

        try:
            list_collections(timeout=10.0, using=self.alias)
        except Exception as e:
            raise ConnectException(f"Connect to Milvus error!{str(e)}")

    def showConnection(self, alias="default", showAll=False):
        from pymilvus import connections

        tempAlias = self.alias if self.alias else alias
        allConnections = connections.list_connections()
        if showAll:
            return tabulate(
                allConnections, headers=["Alias", "Instance"], tablefmt="pretty"
            )
        aliasList = map(lambda x: x[0], allConnections)
        if tempAlias in aliasList:
            host, port = connections.get_connection_addr(tempAlias).values()
            # return """Host: {}\nPort: {}\nAlias: {}""".format(host, port, alias)
            return tabulate(
                [["Host", host], ["Port", port], ["Alias", tempAlias]],
                tablefmt="pretty",
            )
        else:
            return "Connection not found!"

    def _list_collection_names(self, timeout=None):
        from pymilvus import list_collections

        return list(list_collections(timeout, self.alias))

    def _list_partition_names(self, collectionName):
        target = self.getTargetCollection(collectionName)
        result = target.partitions
        return [i.name for i in result]

    def _list_field_names(self, collectionName, showVectorOnly=False):
        target = self.getTargetCollection(collectionName)
        result = target.schema.fields
        if showVectorOnly:
            return reduce(
                lambda x, y: x + [y.name] if y.dtype in [100, 101] else x, result, []
            )
        return [i.name for i in result]

    def _list_index(self, collectionName):
        target = self.getTargetCollection(collectionName)
        try:
            result = target.index()
        except Exception as e:
            return {}
        else:
            details = {
                "field_name": result.field_name,
                "index_type": result.params["index_type"],
                "metric_type": result.params["metric_type"],
                "params": result.params["params"],
            }
            # for p in result.params['params']:
            #     details[p] = result.params['params'][p]
            return details

    def listCollections(self, timeout=None, showLoadedOnly=False):
        result = []
        collectionNames = self._list_collection_names(timeout)
        for name in collectionNames:
            loadingProgress = self.showCollectionLoadingProgress(name)
            loaded, total = loadingProgress.values()
            # isLoaded = (total > 0) and (loaded == total)
            # shouldBeAdded = isLoaded if showLoadedOnly else True
            # if shouldBeAdded:
            result.append([name, "{}/{}".format(loaded, total)])
        return tabulate(
            result,
            headers=["Collection Name", "Entities(Loaded/Total)"],
            tablefmt="grid",
            showindex=True,
        )

    def flushCollectionByNumEntities(self, collectionName):
        col = self.getTargetCollection(collectionName)
        return col.num_entities

    def showCollectionLoadingProgress(self, collectionName, partition_names=None):
        from pymilvus import loading_progress

        self.flushCollectionByNumEntities(collectionName)
        return loading_progress(collectionName, partition_names, self.alias)

    def showIndexBuildingProgress(self, collectionName, index_name=""):
        from pymilvus import index_building_progress

        return index_building_progress(collectionName, index_name, self.alias)

    def getTargetCollection(self, collectionName):
        from pymilvus import Collection

        try:
            target = Collection(collectionName)
        except Exception as e:
            raise ParameterException("Collection error!\n")
        else:
            return target

    def getTargetPartition(self, collectionName, partitionName):
        try:
            targetCollection = self.getTargetCollection(collectionName)
            target = targetCollection.partition(partitionName)
        except Exception as e:
            raise ParameterException("Partition error!\n")
        else:
            return target

    def loadCollection(self, collectionName):
        target = self.getTargetCollection(collectionName)
        target.load()
        result = self.showCollectionLoadingProgress(collectionName)
        return tabulate(
            [
                [
                    collectionName,
                    result.get("num_loaded_entities"),
                    result.get("num_total_entities"),
                ]
            ],
            headers=["Collection Name", "Loaded", "Total"],
            tablefmt="grid",
        )

    def releaseCollection(self, collectionName):
        target = self.getTargetCollection(collectionName)
        target.release()
        result = self.showCollectionLoadingProgress(collectionName)
        return tabulate(
            [
                [
                    collectionName,
                    result.get("num_loaded_entities"),
                    result.get("num_total_entities"),
                ]
            ],
            headers=["Collection Name", "Loaded", "Total"],
            tablefmt="grid",
        )

    def releasePartition(self, collectionName, partitionName):
        targetPartition = self.getTargetPartition(collectionName, partitionName)
        targetPartition.release()
        result = self.showCollectionLoadingProgress(collectionName, [partitionName])
        return result

    def releasePartitions(self, collectionName, partitionNameList):
        result = []
        for name in partitionNameList:
            tmp = self.releasePartition(collectionName, name)
            result.append(
                [name, tmp.get("num_loaded_entities"), tmp.get("num_total_entities")]
            )
        return tabulate(
            result, headers=["Partition Name", "Loaded", "Total"], tablefmt="grid"
        )

    def loadPartition(self, collectionName, partitionName):
        targetPartition = self.getTargetPartition(collectionName, partitionName)
        targetPartition.load()
        result = self.showCollectionLoadingProgress(collectionName, [partitionName])
        return result

    def loadPartitions(self, collectionName, partitionNameList):
        result = []
        for name in partitionNameList:
            tmp = self.loadPartition(collectionName, name)
            result.append(
                [name, tmp.get("num_loaded_entities"), tmp.get("num_total_entities")]
            )
        return tabulate(
            result, headers=["Partition Name", "Loaded", "Total"], tablefmt="grid"
        )

    def listPartitions(self, collectionName):
        target = self.getTargetCollection(collectionName)
        result = target.partitions
        rows = list(map(lambda x: [x.name, x.description], result))
        return tabulate(
            rows,
            headers=["Partition Name", "Description"],
            tablefmt="grid",
            showindex=True,
        )

    def listIndexes(self, collectionName):
        target = self.getTargetCollection(collectionName)
        result = target.indexes
        rows = list(
            map(
                lambda x: [
                    x.field_name,
                    x.params["index_type"],
                    x.params["metric_type"],
                    x.params["params"]["nlist"],
                ],
                result,
            )
        )
        return tabulate(
            rows,
            headers=["Field Name", "Index Type", "Metric Type", "Nlist"],
            tablefmt="grid",
            showindex=True,
        )

    def getCollectionDetails(self, collectionName="", collection=None):
        try:
            target = collection or self.getTargetCollection(collectionName)
        except Exception as e:
            return "Error!\nPlease check your input collection name."
        rows = []
        schema = target.schema
        partitions = target.partitions
        indexes = target.indexes
        fieldSchemaDetails = ""
        for fieldSchema in schema.fields:
            _name = f"{'*' if fieldSchema.is_primary else ''}{fieldSchema.name}"
            _type = DataTypeByNum[fieldSchema.dtype]
            _desc = fieldSchema.description
            _params = fieldSchema.params
            _dim = _params.get("dim")
            _params_desc = f"dim: {_dim}" if _dim else ""
            fieldSchemaDetails += f"\n - {_name} {_type} {_params_desc} {_desc}"
        schemaDetails = """Description: {}\n\nAuto ID: {}\n\nFields(* is the primary field):{}""".format(
            schema.description, schema.auto_id, fieldSchemaDetails
        )
        partitionDetails = "  - " + "\n- ".join(map(lambda x: x.name, partitions))
        indexesDetails = "  - " + "\n- ".join(map(lambda x: x.field_name, indexes))
        rows.append(["Name", target.name])
        rows.append(["Description", target.description])
        rows.append(["Is Empty", target.is_empty])
        rows.append(["Entities", target.num_entities])
        rows.append(["Primary Field", target.primary_field.name])
        rows.append(["Schema", schemaDetails])
        rows.append(["Partitions", partitionDetails])
        rows.append(["Indexes", indexesDetails])
        return tabulate(rows, tablefmt="grid")

    def getPartitionDetails(self, collection, partitionName=""):
        partition = collection.partition(partitionName)
        if not partition:
            return "No such partition!"
        rows = []
        rows.append(["Partition Name", partition.name])
        rows.append(["Description", partition.description])
        rows.append(["Is empty", partition.is_empty])
        rows.append(["Number of Entities", partition.num_entities])
        return tabulate(rows, tablefmt="grid")

    def getIndexDetails(self, collection):
        index = collection.index()
        if not index:
            return "No index!"
        rows = []
        rows.append(["Corresponding Collection", index.collection_name])
        rows.append(["Corresponding Field", index.field_name])
        rows.append(["Index Type", index.params["index_type"]])
        rows.append(["Metric Type", index.params["metric_type"]])
        params = index.params["params"]
        paramsDetails = "\n- ".join(map(lambda k: f"{k[0]}: {k[1]}", params.items()))
        rows.append(["Params", paramsDetails])
        return tabulate(rows, tablefmt="grid")

    def createCollection(
        self, collectionName, primaryField, autoId, description, fields
    ):
        from pymilvus import Collection, DataType, FieldSchema, CollectionSchema

        fieldList = []
        for field in fields:
            [fieldName, fieldType, fieldData] = field.split(":")
            isVector = False
            if fieldType in ["BINARY_VECTOR", "FLOAT_VECTOR"]:
                fieldList.append(
                    FieldSchema(
                        name=fieldName, dtype=DataType[fieldType], dim=int(fieldData)
                    )
                )
            else:
                fieldList.append(
                    FieldSchema(
                        name=fieldName, dtype=DataType[fieldType], description=fieldData
                    )
                )
        schema = CollectionSchema(
            fields=fieldList,
            primary_field=primaryField,
            auto_id=autoId,
            description=description,
        )
        collection = Collection(name=collectionName, schema=schema)
        return self.getCollectionDetails(collection=collection)

    def createPartition(self, collectionName, description, partitionName):
        collection = self.getTargetCollection(collectionName)
        collection.create_partition(partitionName, description=description)
        return self.getPartitionDetails(collection, partitionName)

    def createIndex(
        self, collectionName, fieldName, indexType, metricType, params, timeout
    ):
        collection = self.getTargetCollection(collectionName)
        indexParams = {}
        for param in params:
            paramList = param.split(":")
            [paramName, paramValue] = paramList
            indexParams[paramName] = int(paramValue)
        index = {
            "index_type": indexType,
            "params": indexParams,
            "metric_type": metricType,
        }
        collection.create_index(fieldName, index, timeout=timeout)
        return self.getIndexDetails(collection)

    def isCollectionExist(self, collectionName):
        from pymilvus import has_collection

        return has_collection(collectionName, using=self.alias)

    def isPartitionExist(self, collection, partitionName):
        return collection.has_partition(partitionName)

    def isIndexExist(self, collection):
        return collection.has_index()

    def dropCollection(self, collectionName, timeout):
        collection = self.getTargetCollection(collectionName)
        collection.drop(timeout=timeout)
        return self.isCollectionExist(collectionName)

    def dropPartition(self, collectionName, partitionName, timeout):
        collection = self.getTargetCollection(collectionName)
        collection.drop_partition(partitionName, timeout=timeout)
        return self.isPartitionExist(collection, partitionName)

    def dropIndex(self, collectionName, timeout):
        collection = self.getTargetCollection(collectionName)
        collection.drop_index(timeout=timeout)
        return self.isIndexExist(collection)

    def search(self, collectionName, searchParameters, prettierFormat=True):
        collection = self.getTargetCollection(collectionName)
        collection.load()
        res = collection.search(**searchParameters)
        if not prettierFormat:
            return res
        # hits = res[0]
        results = []
        for hits in res:
            results += [
                tabulate(
                    map(lambda x: [x.id, x.distance, x.score], hits),
                    headers=["Index", "ID", "Distance", "Score"],
                    tablefmt="grid",
                    showindex=True,
                )
            ]
        # return tabulate(map(lambda x: [x.id, x.distance], hits), headers=['Index', 'ID', 'Distance'], tablefmt='grid', showindex=True)
        return results

    def query(self, collectionName, queryParameters):
        collection = self.getTargetCollection(collectionName)
        collection.load()
        res = collection.query(**queryParameters)
        # return f"- Query results: {res}"
        if not len(res):
            return f"- Query results: {res}"
        headers = [i for i in res[0]]
        return tabulate(
            [[_[i] for i in _] for _ in res],
            headers=headers,
            tablefmt="grid",
            showindex=True,
        )

    def insert(self, collectionName, data, partitionName=None, timeout=None):
        collection = self.getTargetCollection(collectionName)
        result = collection.insert(data, partition_name=partitionName, timeout=timeout)
        entitiesNum = collection.num_entities
        return [result, entitiesNum]

    def importData(self, collectionName, data, partitionName=None, timeout=None):
        [result, entitiesNum] = self.insert(
            collectionName, data, partitionName, timeout
        )
        insert_count = result.insert_count
        timestamp = result.timestamp
        prettierResult = []
        prettierResult.append(["Total insert entities: ", insert_count])
        prettierResult.append(["Total collection entities: ", entitiesNum])
        prettierResult.append(["Milvus timestamp: ", timestamp])
        return tabulate(prettierResult)

    def calcDistance(self, vectors_left, vectors_right, params=None, timeout=None):
        from pymilvus import utility

        result = utility.calc_distance(
            vectors_left, vectors_right, params, timeout, using=self.alias
        )
        return result

    def deleteEntities(self, expr, collectionName, partition_name=None, timeout=None):
        collection = self.getTargetCollection(collectionName)
        result = collection.delete(expr, partition_name=partition_name, timeout=timeout)
        return result

    def getQuerySegmentInfo(self, collectionName, timeout=None, prettierFormat=False):
        from pymilvus import utility

        result = utility.get_query_segment_info(
            collectionName, timeout=timeout, using=self.alias
        )
        if not prettierFormat or not result:
            return result
        firstChild = result[0]
        headers = ["segmentID", "collectionID", "partitionID", "mem_size", "num_rows"]
        return tabulate(
            [[getattr(_, i) for i in headers] for _ in result],
            headers=headers,
            showindex=True,
        )

    def createCollectionAlias(
        self, collectionName, collectionAliasName="", timeout=None
    ):
        collection = self.getTargetCollection(collectionName)
        result = collection.create_alias(collectionAliasName, timeout=timeout)
        return result

    def dropCollectionAlias(self, collectionName, collectionAliasName="", timeout=None):
        collection = self.getTargetCollection(collectionName)
        result = collection.drop_alias(collectionAliasName, timeout=timeout)
        return result

    def alterCollectionAlias(
        self, collectionName, collectionAliasName="", timeout=None
    ):
        collection = self.getTargetCollection(collectionName)
        result = collection.alter_alias(collectionAliasName, timeout=timeout)
        return result

    def createCollectionAliasList(self, collectionName, aliasList=None, timeout=None):
        aliasList = aliasList if aliasList is not None else []
        collection = self.getTargetCollection(collectionName)
        result = []
        for aliasItem in aliasList:
            aliasResult = collection.create_alias(aliasItem, timeout=timeout)
            result.append(aliasResult)
        return result

    def alterCollectionAliasList(self, collectionName, aliasList=None, timeout=None):
        aliasList = aliasList if aliasList is not None else []
        collection = self.getTargetCollection(collectionName)
        result = []
        for aliasItem in aliasList:
            aliasResult = collection.alter_alias(aliasItem, timeout=timeout)
            result.append(aliasResult)
        return result

    # def loadBalance(self, src_node_id, dst_node_ids, sealed_segment_ids, timeout=None):
    #     from pymilvus import utility
    #     utility.load_balance(src_node_id, dst_node_ids, sealed_segment_ids, timeout=timeout)


class Completer(object):
    # COMMANDS = ['clear', 'connect', 'create', 'delete', 'describe', 'exit',
    #         'list', 'load', 'query', 'release', 'search', 'show', 'version' ]
    RE_SPACE = re.compile(".*\s+$", re.M)
    CMDS_DICT = {
        "calc": [],
        "clear": [],
        "connect": [],
        "create": ["alias", "collection", "partition", "index"],
        "delete": ["alias", "collection", "partition", "index"],
        "describe": ["collection", "partition", "index"],
        "exit": [],
        "help": [],
        "import": [],
        "list": ["collections", "partitions", "indexes"],
        "load": [],
        "query": [],
        "release": [],
        "search": [],
        "show": ["connection", "index_progress", "loading_progress", "query_segment"],
        "version": [],
    }

    def __init__(self) -> None:
        super().__init__()
        self.COMMANDS = list(self.CMDS_DICT.keys())
        self.createCompleteFuncs(self.CMDS_DICT)

    def createCompleteFuncs(self, cmdDict):
        for cmd in cmdDict:
            sub_cmds = cmdDict[cmd]
            complete_example = self.makeComplete(cmd, sub_cmds)
            setattr(self, "complete_%s" % cmd, complete_example)

    def makeComplete(self, cmd, sub_cmds):
        def f_complete(args):
            f"Completions for the {cmd} command."
            if not args:
                return self._complete_path(".")
            if len(args) <= 1 and not cmd == "import":
                return self._complete_2nd_level(sub_cmds, args[-1])
            return self._complete_path(args[-1])

        return f_complete

    def _listdir(self, root):
        "List directory 'root' appending the path separator to subdirs."
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def _complete_path(self, path=None):
        "Perform completion of filesystem path."
        if not path:
            return self._listdir(".")
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else "."
        res = [
            os.path.join(dirname, p) for p in self._listdir(tmp) if p.startswith(rest)
        ]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + " "]

    def _complete_2nd_level(self, SUB_COMMANDS=[], cmd=None):
        if not cmd:
            return [c + " " for c in SUB_COMMANDS]
        res = [c for c in SUB_COMMANDS if c.startswith(cmd)]
        if len(res) > 1 or not (cmd in SUB_COMMANDS):
            return res
        return [cmd + " "]

    # def complete_create(self, args):
    #     "Completions for the 'create' command."
    #     if not args:
    #         return self._complete_path('.')
    #     sub_cmds = ['collection', 'partition', 'index']
    #     if len(args) <= 1:
    #         return self._complete_2nd_level(sub_cmds, args[-1])
    #     return self._complete_path(args[-1])

    def complete(self, text, state):
        "Generic readline completion entry point."
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        # show all commands
        if not line:
            return [c + " " for c in self.COMMANDS][state]
        # account for last argument ending in a space
        if self.RE_SPACE.match(buffer):
            line.append("")
        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in self.COMMANDS:
            impl = getattr(self, "complete_%s" % cmd)
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + " "][state]
        results = [c + " " for c in self.COMMANDS if c.startswith(cmd)] + [None]
        return results[state]


WELCOME_MSG = """
                                               
                                               
  __  __ _ _                    ____ _     ___ 
 |  \/  (_) |_   ___   _ ___   / ___| |   |_ _|
 | |\/| | | \ \ / / | | / __| | |   | |    | | 
 | |  | | | |\ V /| |_| \__ \ | |___| |___ | | 
 |_|  |_|_|_| \_/  \__,_|___/  \____|_____|___|
                                               
                                               
Learn more: https://github.com/milvus-io/milvus_cli.

"""

EXIT_MSG = "\n\nThanks for using.\nWe hope your feedback: https://github.com/milvus-io/milvus_cli/issues/new.\n\n"
