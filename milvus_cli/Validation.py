from Types import ParameterException
from Types import FiledDataTypes, IndexTypes, IndexTypesMap, SearchParams, MetricTypes
from Fs import readCsvFile


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
    # if not params:
    #     raise ParameterException('Missing params')
    paramNames = []
    buildingParameters = IndexTypesMap[indexType]['index_building_parameters']
    for param in params:
        paramList = param.split(':')
        if not (len(paramList) == 2):
            raise ParameterException(
                'Params should contain two paremeters and concat by ":".')
        [paramName, paramValue] = paramList
        paramNames.append(paramName)
        if paramName not in buildingParameters:
            raise ParameterException(
                'Invalid index param, should be one of {}'.format(str(buildingParameters)))
        try:
            int(paramValue)
        except ValueError as e:
            raise ParameterException("""Index param's value should be int.""")
    # Dedup field name.
    newNames = list(set(paramNames))
    if not (len(newNames) == len(paramNames)):
        raise ParameterException('Index params are duplicated.')


def validateSearchParams(data, annsField, metricType, params, limit, expr, partitionNames, timeout, roundDecimal, hasIndex=True):
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
    if hasIndex:
        # Validate metricType
        if metricType not in MetricTypes:
            raise ParameterException(
                'Invalid index metric type, should be one of {}'.format(str(MetricTypes)))
        # Validate params
        paramDict = {}
        if type(params) == str:
            paramsList = params.replace(' ', '').split(',')
        else:
            paramsList = params
        for param in paramsList:
            if not param:
                continue
            paramList = param.split(':')
            if not (len(paramList) == 2):
                raise ParameterException(
                    'Params should contain two paremeters and concat by ":".')
            [paramName, paramValue] = paramList
            if paramName not in SearchParams:
                raise ParameterException(
                    'Invalid search parameter, should be one of {}'.format(str(SearchParams)))
            try:
                paramDict[paramName] = int(paramValue)
            except ValueError as e:
                raise ParameterException(
                    """Search parameter's value should be int.""")
        result['param'] = {"metric_type": metricType}
        if paramDict.keys():
            result['param']['params'] = paramDict
    else:
        result['param'] = {}
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
    if roundDecimal:
        result['round_decimal'] = int(roundDecimal)
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
