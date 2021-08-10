class ParameterException(Exception):
    "Custom Exception for parameters checking."

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
    "PQM"
]

MetricTypes = [
    "L2",
    "IP",
    "HAMMING",
    "TANIMOTO"
]


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
