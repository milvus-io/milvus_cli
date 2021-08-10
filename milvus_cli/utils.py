class ParameterException(Exception):
    "Custom Exception for parameters checking."

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


FiledDataType = [
    'BOOL',
    'INT8',
    'INT16',
    'INT32',
    'INT64',
    'FLOAT',
    'DOUBLE',
    'STRING',
    'BINARY_VECTOR',
    'FLOAT_VECTOR', ]


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
        if fieldType not in FiledDataType:
            raise ParameterException(
                'Error field data type, should be one of {}'.format(str(FiledDataType)))
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
        raise ParameterException("""Primary field name doesn't exist in input fields.""")
