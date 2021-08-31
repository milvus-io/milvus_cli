from tabulate import tabulate
import readline
import re
import os


def getPackageVersion():
    import pkg_resources  # part of setuptools
    return pkg_resources.require("milvus_cli")[0].version


class ParameterException(Exception):
    "Custom Exception for parameters checking."

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


class ConnectException(Exception):
    "Custom Exception for milvus connection."

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


FiledDataTypes = [
    "BOOL",
    "INT8",
    "INT16",
    "INT32",
    "INT64",
    "FLOAT",
    "DOUBLE",
    "STRING",
    "BINARY_VECTOR",
    "FLOAT_VECTOR"
]

IndexTypes = [
    "FLAT",
    "IVF_FLAT",
    "IVF_SQ8",
    # "IVF_SQ8_HYBRID",
    "IVF_PQ",
    "HNSW",
    # "NSG",
    "ANNOY",
    "RHNSW_FLAT",
    "RHNSW_PQ",
    "RHNSW_SQ",
    "BIN_FLAT",
    "BIN_IVF_FLAT"
]

IndexParams = [
    "nlist",
    "m",
    "nbits",
    "M",
    "efConstruction",
    "n_trees",
    "PQM",
    "nprobe"
]

MetricTypes = [
    "L2",
    "IP",
    "HAMMING",
    "TANIMOTO"
]

DataTypeByNum = {
    0: 'NONE',
    1: 'BOOL',
    2: 'INT8',
    3: 'INT16',
    4: 'INT32',
    5: 'INT64',
    10: 'FLOAT',
    11: 'DOUBLE',
    20: 'STRING',
    100: 'BINARY_VECTOR',
    101: 'FLOAT_VECTOR',
    999: 'UNKNOWN',
}


def validateParamsByCustomFunc(customFunc, errMsg, *params):
    try:
        customFunc(*params)
    except Exception as e:
        raise ParameterException(f"{errMsg}")


def validateCollectionParameter(collectionName, primaryField, fields):
    if not collectionName:
        raise ParameterException('Missing collection name.')
    if not primaryField:
        raise ParameterException('Missing primary field.')
    if not fields:
        raise ParameterException('Missing fields.')
    fieldNames = []
    for field in fields:
        fieldList = field.split(':')
        if not (len(fieldList) == 3):
            raise ParameterException(
                'Field should contain three paremeters and concat by ":".')
        [fieldName, fieldType, fieldData] = fieldList
        fieldNames.append(fieldName)
        if fieldType not in FiledDataTypes:
            raise ParameterException(
                'Invalid field data type, should be one of {}'.format(str(FiledDataTypes)))
        if fieldType in ['BINARY_VECTOR', 'FLOAT_VECTOR']:
            try:
                int(fieldData)
            except ValueError as e:
                raise ParameterException("""Vector's dim should be int.""")
    # Dedup field name.
    newNames = list(set(fieldNames))
    if not (len(newNames) == len(fieldNames)):
        raise ParameterException('Field names are duplicated.')
    if primaryField not in fieldNames:
        raise ParameterException(
            """Primary field name doesn't exist in input fields.""")


def validateIndexParameter(indexType, metricType, params):
    if indexType not in IndexTypes:
        raise ParameterException(
            'Invalid index type, should be one of {}'.format(str(IndexTypes)))
    if metricType not in MetricTypes:
        raise ParameterException(
            'Invalid index metric type, should be one of {}'.format(str(MetricTypes)))
    if not params:
        raise ParameterException('Missing params')
    paramNames = []
    for param in params:
        paramList = param.split(':')
        if not (len(paramList) == 2):
            raise ParameterException(
                'Params should contain two paremeters and concat by ":".')
        [paramName, paramValue] = paramList
        paramNames.append(paramName)
        if paramName not in IndexParams:
            raise ParameterException(
                'Invalid index param, should be one of {}'.format(str(IndexParams)))
        try:
            int(paramValue)
        except ValueError as e:
            raise ParameterException("""Index param's value should be int.""")
    # Dedup field name.
    newNames = list(set(paramNames))
    if not (len(newNames) == len(paramNames)):
        raise ParameterException('Index params are duplicated.')


def validateSearchParams(data, annsField, metricType, params, limit, expr, partitionNames, timeout):
    import json
    result = {}
    # Validate data
    try:
        if '.csv' in data:
            csvData = readCsvFile(data, withCol=False)
            result['data'] = csvData['data'][0]
        else:
            result['data'] = json.loads(
                data.replace('\'', '').replace('\"', ''))
    except Exception as e:
        raise ParameterException(
            'Format(list[list[float]]) "Data" error! {}'.format(str(e)))
    # Validate annsField
    if not annsField:
        raise ParameterException('annsField is empty!')
    result['anns_field'] = annsField
    # Validate metricType
    if metricType not in MetricTypes:
        raise ParameterException(
            'Invalid index metric type, should be one of {}'.format(str(MetricTypes)))
    # Validate params
    paramDict = {}
    paramsList = params.replace(' ', '').split(',')
    for param in paramsList:
        if not param:
            continue
        paramList = param.split(':')
        if not (len(paramList) == 2):
            raise ParameterException(
                'Params should contain two paremeters and concat by ":".')
        [paramName, paramValue] = paramList
        paramDict[paramName] = paramValue
        if paramName not in IndexParams:
            raise ParameterException(
                'Invalid search parameter, should be one of {}'.format(str(IndexParams)))
        try:
            int(paramValue)
        except ValueError as e:
            raise ParameterException(
                """Search parameter's value should be int.""")
    result['param'] = {"metric_type": metricType}
    if paramDict.keys():
        result['param']['params'] = paramDict
    #  Validate limit
    try:
        result['limit'] = int(limit)
    except Exception as e:
        raise ParameterException(
            'Format(int) "limit" error! {}'.format(str(e)))
    # Validate expr
    result['expr'] = expr
    # Validate partitionNames
    if partitionNames:
        try:
            result['partition_names'] = partitionNames.replace(
                ' ', '').split(',')
        except Exception as e:
            raise ParameterException(
                'Format(list[str]) "partitionNames" error! {}'.format(str(e)))
    # Validate timeout
    if timeout:
        result['timeout'] = float(timeout)
    return result


def validateQueryParams(expr, partitionNames, outputFields, timeout):
    result = {}
    if not expr:
        raise ParameterException('expr is empty!')
    if ' in ' not in expr:
        raise ParameterException(
            'expr only accepts "<field_name> in [<min>,<max>]"!')
    result['expr'] = expr
    if not outputFields:
        result['output_fields'] = None
    else:
        nameList = outputFields.replace(' ', '').split(',')
        result['output_fields'] = nameList
    if not partitionNames:
        result['partition_names'] = None
    else:
        nameList = partitionNames.replace(' ', '').split(',')
        result['partition_names'] = nameList
    result['timeout'] = float(timeout) if timeout else None
    return result


def checkEmpty(x): return not not x


class PyOrm(object):
    host = '127.0.0.1'
    port = 19530
    alias = 'default'

    def connect(self, alias=None, host=None, port=None):
        self.alias = alias
        self.host = host
        self.port = port
        from pymilvus import connections
        connections.connect(self.alias, host=self.host, port=self.port)

    def checkConnection(self):
        from pymilvus import list_collections
        try:
            list_collections(timeout=10.0, using=self.alias)
        except Exception as e:
            raise ConnectException(f'Connect to Milvus error!{str(e)}')

    def showConnection(self, alias="default", showAll=False):
        from pymilvus import connections
        tempAlias = self.alias if self.alias else alias
        allConnections = connections.list_connections()
        if showAll:
            return tabulate(allConnections, headers=['Alias', 'Instance'], tablefmt='pretty')
        aliasList = map(lambda x: x[0], allConnections)
        if tempAlias in aliasList:
            host, port = connections.get_connection_addr(tempAlias).values()
            # return """Host: {}\nPort: {}\nAlias: {}""".format(host, port, alias)
            return tabulate([['Host', host], ['Port', port], ['Alias', tempAlias]], tablefmt='pretty')
        else:
            return "Connection not found!"

    def listCollections(self, timeout=None, showLoadedOnly=False):
        from pymilvus import list_collections
        result = []
        collectionNames = list_collections(timeout, self.alias)
        for name in collectionNames:
            loadingProgress = self.showCollectionLoadingProgress(name)
            loaded, total = loadingProgress.values()
            # isLoaded = (total > 0) and (loaded == total)
            # shouldBeAdded = isLoaded if showLoadedOnly else True
            # if shouldBeAdded:
            result.append([name, "{}/{}".format(loaded, total)])
        return tabulate(result, headers=['Collection Name', 'Entities(Loaded/Total)'], tablefmt='grid', showindex=True)

    def showCollectionLoadingProgress(self, collectionName, partition_names=None):
        from pymilvus import loading_progress
        return loading_progress(collectionName, partition_names, self.alias)

    def showIndexBuildingProgress(self, collectionName, index_name=""):
        from pymilvus import index_building_progress
        return index_building_progress(collectionName, index_name, self.alias)

    def getTargetCollection(self, collectionName):
        from pymilvus import Collection
        try:
            target = Collection(collectionName)
        except Exception as e:
            raise ParameterException('Collection error!\n')
        else:
            return target

    def loadCollection(self, collectionName):
        target = self.getTargetCollection(collectionName)
        target.load()
        result = self.showCollectionLoadingProgress(collectionName)
        return tabulate([[collectionName, result.get('num_loaded_entities'), result.get('num_total_entities')]], headers=['Collection Name', 'Loaded', 'Total'], tablefmt='grid')

    def releaseCollection(self, collectionName):
        target = self.getTargetCollection(collectionName)
        target.release()
        result = self.showCollectionLoadingProgress(collectionName)
        return tabulate([[collectionName, result.get('num_loaded_entities'), result.get('num_total_entities')]], headers=['Collection Name', 'Loaded', 'Total'], tablefmt='grid')

    def listPartitions(self, collectionName):
        target = self.getTargetCollection(collectionName)
        result = target.partitions
        rows = list(map(lambda x: [x.name, x.description], result))
        return tabulate(rows, headers=['Partition Name', 'Description'], tablefmt='grid', showindex=True)

    def listIndexes(self, collectionName):
        target = self.getTargetCollection(collectionName)
        result = target.indexes
        rows = list(map(lambda x: [x.field_name, x.params['index_type'],
                    x.params['metric_type'], x.params['params']['nlist']], result))
        return tabulate(rows, headers=['Field Name', 'Index Type', 'Metric Type', 'Nlist'], tablefmt='grid', showindex=True)

    def getCollectionDetails(self, collectionName='', collection=None):
        try:
            target = collection or self.getTargetCollection(collectionName)
        except Exception as e:
            return "Error!\nPlease check your input collection name."
        rows = []
        schema = target.schema
        partitions = target.partitions
        indexes = target.indexes
        fieldSchemaDetails = ''
        for fieldSchema in schema.fields:
            _name = f"{'*' if fieldSchema.is_primary else ''}{fieldSchema.name}"
            _type = DataTypeByNum[fieldSchema.dtype]
            _desc = fieldSchema.description
            _params = fieldSchema.params
            _dim = _params.get('dim')
            _params_desc = f"dim: {_dim}" if _dim else ""
            fieldSchemaDetails += f"\n - {_name} {_type} {_params_desc} {_desc}"
        schemaDetails = """Description: {}\n\nAuto ID: {}\n\nFields(* is the primary field):{}""".format(
            schema.description, schema.auto_id, fieldSchemaDetails)
        partitionDetails = "  - " + \
            "\n- ".join(map(lambda x: x.name, partitions))
        indexesDetails = "  - " + \
            "\n- ".join(map(lambda x: x.field_name, indexes))
        rows.append(['Name', target.name])
        rows.append(['Description', target.description])
        rows.append(['Is Empty', target.is_empty])
        rows.append(['Entities', target.num_entities])
        rows.append(['Primary Field', target.primary_field.name])
        rows.append(['Schema', schemaDetails])
        rows.append(['Partitions', partitionDetails])
        rows.append(['Indexes', indexesDetails])
        return tabulate(rows, tablefmt='grid')

    def getPartitionDetails(self, collection, partitionName=''):
        partition = collection.partition(partitionName)
        if not partition:
            return "No such partition!"
        rows = []
        rows.append(['Partition Name', partition.name])
        rows.append(['Description', partition.description])
        rows.append(['Is empty', partition.is_empty])
        rows.append(['Number of Entities', partition.num_entities])
        return tabulate(rows, tablefmt='grid')

    def getIndexDetails(self, collection):
        index = collection.index()
        if not index:
            return "No index!"
        rows = []
        rows.append(['Corresponding Collection', index.collection_name])
        rows.append(['Corresponding Field', index.field_name])
        rows.append(['Index Type', index.params['index_type']])
        rows.append(['Metric Type', index.params['metric_type']])
        rows.append(['Params', index.params['params']])
        return tabulate(rows, tablefmt='grid')

    def createCollection(self, collectionName, primaryField, autoId, description, fields):
        from pymilvus import Collection, DataType, FieldSchema, CollectionSchema
        fieldList = []
        for field in fields:
            [fieldName, fieldType, fieldData] = field.split(':')
            isVector = False
            if fieldType in ['BINARY_VECTOR', 'FLOAT_VECTOR']:
                fieldList.append(FieldSchema(
                    name=fieldName, dtype=DataType[fieldType], dim=int(fieldData)))
            else:
                fieldList.append(FieldSchema(
                    name=fieldName, dtype=DataType[fieldType], description=fieldData))
        schema = CollectionSchema(
            fields=fieldList, primary_field=primaryField, auto_id=autoId, description=description)
        collection = Collection(name=collectionName, schema=schema)
        return self.getCollectionDetails(collection=collection)

    def createPartition(self, collectionName, description, partitionName):
        collection = self.getTargetCollection(collectionName)
        collection.create_partition(partitionName, description=description)
        return self.getPartitionDetails(collection, partitionName)

    def createIndex(self, collectionName, fieldName, indexType, metricType, params, timeout):
        collection = self.getTargetCollection(collectionName)
        indexParams = {}
        for param in params:
            paramList = param.split(':')
            [paramName, paramValue] = paramList
            indexParams[paramName] = int(paramValue)
        index = {"index_type": indexType,
                 "params": indexParams, "metric_type": metricType}
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

    def search(self, collectionName, searchParameters):
        collection = self.getTargetCollection(collectionName)
        collection.load()
        res = collection.search(**searchParameters)
        hits = res[0]
        return tabulate(map(lambda x: [x.id, x.distance], hits), headers=['Index', 'ID', 'Distance'], tablefmt='grid', showindex=True)

    def query(self, collectionName, queryParameters):
        collection = self.getTargetCollection(collectionName)
        collection.load()
        res = collection.query(**queryParameters)
        # return f"- Query results: {res}"
        if not len(res):
            return f"- Query results: {res}"
        headers = [i for i in res[0]]
        return tabulate([[_[i] for i in _] for _ in res], headers=headers, tablefmt='grid', showindex=True)

    def insert(self, collectionName, data, partitionName=None, timeout=None):
        collection = self.getTargetCollection(collectionName)
        collection.insert(data, partition_name=partitionName, timeout=timeout)


class Completer(object):
    # COMMANDS = ['clear', 'connect', 'create', 'delete', 'describe', 'exit',
    #         'list', 'load', 'query', 'release', 'search', 'show', 'version' ]
    RE_SPACE = re.compile('.*\s+$', re.M)
    CMDS_DICT = {
        'clear': [],
        'connect': [],
        'create': ['collection', 'partition', 'index'],
        'delete': ['collection', 'partition', 'index'],
        'describe': ['collection', 'partition'],
        'exit': [],
        'help': [],
        'import': [],
        'list': ['collections', 'partitions', 'indexes'],
        'load': [],
        'query': [],
        'release': [],
        'search': [],
        'show': ['connection', 'index_progress', 'loading_progress'],
        'version': [],
    }

    def __init__(self) -> None:
        super().__init__()
        self.COMMANDS = list(self.CMDS_DICT.keys())
        self.createCompleteFuncs(self.CMDS_DICT)

    def createCompleteFuncs(self, cmdDict):
        for cmd in cmdDict:
            sub_cmds = cmdDict[cmd]
            complete_example = self.makeComplete(cmd, sub_cmds)
            setattr(self, 'complete_%s' % cmd, complete_example)

    def makeComplete(self, cmd, sub_cmds):
        def f_complete(args):
            f"Completions for the {cmd} command."
            if not args:
                return self._complete_path('.')
            if len(args) <= 1 and not cmd == 'import':
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
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
               for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def _complete_2nd_level(self, SUB_COMMANDS=[], cmd=None):
        if not cmd:
            return [c + ' ' for c in SUB_COMMANDS]
        res = [c for c in SUB_COMMANDS if c.startswith(cmd)]
        if len(res) > 1 or not (cmd in SUB_COMMANDS):
            return res
        return [cmd + ' ']

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
            return [c + ' ' for c in self.COMMANDS][state]
        # account for last argument ending in a space
        if self.RE_SPACE.match(buffer):
            line.append('')
        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in self.COMMANDS:
            impl = getattr(self, 'complete_%s' % cmd)
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + ' '][state]
        results = [
            c + ' ' for c in self.COMMANDS if c.startswith(cmd)] + [None]
        return results[state]


def readCsvFile(path='', withCol=True):
    if not path or not path[-4:] == '.csv':
        raise ParameterException('Path is empty or target file is not .csv')
    fileSize = os.stat(path).st_size
    if fileSize >= 512000000:
        raise ParameterException(
            'File is too large! Only allow csv files less than 512MB.')
    from csv import reader
    from json import JSONDecodeError
    import click
    try:
        result = {'columns': [], 'data': []}
        with click.open_file(path, 'r') as csv_file:
            click.echo(f'Opening csv file({fileSize} bytes)...')
            csv_reader = reader(csv_file, delimiter=',')
            # For progressbar, transform it to list.
            rows = list(csv_reader)
            line_count = 0
            with click.progressbar(rows, label='Reading csv rows...', show_percent=True) as bar:
                # for row in csv_reader:
                for row in bar:
                    if withCol and line_count == 0:
                        result['columns'] = row
                        line_count += 1
                    else:
                        formatRowForData(row, result['data'])
                        line_count += 1
            click.echo(f'''Column names are {result['columns']}''')
            click.echo(f'Processed {line_count} lines.')
    except FileNotFoundError as fe:
        raise ParameterException(f'FileNotFoundError {str(fe)}')
    except UnicodeDecodeError as ue:
        raise ParameterException(f'UnicodeDecodeError {str(ue)}')
    except JSONDecodeError as je:
        raise ParameterException(f'JSONDecodeError {str(je)}')
    else:
        return result


# For readCsvFile formatting data.
def formatRowForData(row=[], data=[]):
    from json import loads
    # init data with empty list
    if not data:
        for _in in range(len(row)):
            data.append([])
    for idx, val in enumerate(row):
        formattedVal = loads(val)
        data[idx].append(formattedVal)
