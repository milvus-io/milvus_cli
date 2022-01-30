from Types import ParameterException
from Types import (
    FiledDataTypes,
    IndexTypes,
    IndexTypesMap,
    SearchParams,
    MetricTypes,
    Operators,
)
from Fs import readCsvFile


def validateParamsByCustomFunc(customFunc, errMsg, *params):
    try:
        customFunc(*params)
    except Exception as e:
        raise ParameterException(f"{errMsg}")


def validateCollectionParameter(collectionName, primaryField, fields):
    if not collectionName:
        raise ParameterException("Missing collection name.")
    if not primaryField:
        raise ParameterException("Missing primary field.")
    if not fields:
        raise ParameterException("Missing fields.")
    fieldNames = []
    for field in fields:
        fieldList = field.split(":")
        if len(fieldList) != 3:
            raise ParameterException(
                'Field should contain three paremeters and concat by ":".'
            )
        [fieldName, fieldType, fieldData] = fieldList
        fieldNames.append(fieldName)
        if fieldType not in FiledDataTypes:
            raise ParameterException(
                "Invalid field data type, should be one of {}".format(
                    str(FiledDataTypes)
                )
            )
        if fieldType in ["BINARY_VECTOR", "FLOAT_VECTOR"]:
            try:
                int(fieldData)
            except ValueError as e:
                raise ParameterException("""Vector's dim should be int.""")
    # Dedup field name.
    newNames = list(set(fieldNames))
    if len(newNames) != len(fieldNames):
        raise ParameterException("Field names are duplicated.")
    if primaryField not in fieldNames:
        raise ParameterException(
            """Primary field name doesn't exist in input fields."""
        )


def validateIndexParameter(indexType, metricType, params):
    if indexType not in IndexTypes:
        raise ParameterException(
            "Invalid index type, should be one of {}".format(str(IndexTypes))
        )
    if metricType not in MetricTypes:
        raise ParameterException(
            "Invalid index metric type, should be one of {}".format(str(MetricTypes))
        )
    # if not params:
    #     raise ParameterException('Missing params')
    paramNames = []
    buildingParameters = IndexTypesMap[indexType]["index_building_parameters"]
    for param in params:
        paramList = param.split(":")
        if len(paramList) != 2:
            raise ParameterException(
                'Params should contain two paremeters and concat by ":".'
            )
        [paramName, paramValue] = paramList
        paramNames.append(paramName)
        if paramName not in buildingParameters:
            raise ParameterException(
                "Invalid index param, should be one of {}".format(
                    str(buildingParameters)
                )
            )
        try:
            int(paramValue)
        except ValueError as e:
            raise ParameterException("""Index param's value should be int.""")
    # Dedup field name.
    newNames = list(set(paramNames))
    if len(newNames) != len(paramNames):
        raise ParameterException("Index params are duplicated.")


def validateSearchParams(
    data,
    annsField,
    metricType,
    params,
    limit,
    expr,
    partitionNames,
    timeout,
    roundDecimal,
    hasIndex=True,
    guarantee_timestamp=None,
    travel_timestamp=None,
):
    import json

    result = {}
    # Validate data
    try:
        if ".csv" in data:
            csvData = readCsvFile(data, withCol=False)
            result["data"] = csvData["data"][0]
        else:
            result["data"] = json.loads(data.replace("'", "").replace('"', ""))
    except Exception as e:
        raise ParameterException(
            'Format(list[list[float]]) "Data" error! {}'.format(str(e))
        )
    # Validate annsField
    if not annsField:
        raise ParameterException("annsField is empty!")
    result["anns_field"] = annsField
    if hasIndex:
        # Validate metricType
        if metricType not in MetricTypes:
            raise ParameterException(
                "Invalid index metric type, should be one of {}".format(
                    str(MetricTypes)
                )
            )
        # Validate params
        paramDict = {}
        if isinstance(params, str):
            paramsList = params.replace(" ", "").split(",")
        else:
            paramsList = params
        for param in paramsList:
            if not param:
                continue
            paramList = param.split(":")
            if len(paramList) != 2:
                raise ParameterException(
                    'Params should contain two paremeters and concat by ":".'
                )
            [paramName, paramValue] = paramList
            if paramName not in SearchParams:
                raise ParameterException(
                    f"Invalid search parameter, should be one of {SearchParams}"
                )
            try:
                paramDict[paramName] = int(paramValue)
            except ValueError as e:
                raise ParameterException("""Search parameter's value should be int.""")
        result["param"] = {"metric_type": metricType}
        if paramDict.keys():
            result["param"]["params"] = paramDict
    else:
        result["param"] = {}
    #  Validate limit
    try:
        result["limit"] = int(limit)
    except Exception as e:
        raise ParameterException('Format(int) "limit" error! {}'.format(str(e)))
    # Validate expr
    result["expr"] = expr if expr else None
    # Validate partitionNames
    if partitionNames:
        try:
            result["partition_names"] = partitionNames.replace(" ", "").split(",")
        except Exception as e:
            raise ParameterException(
                'Format(list[str]) "partitionNames" error! {}'.format(str(e))
            )
    # Validate timeout
    if timeout:
        result["timeout"] = float(timeout)
    if roundDecimal:
        result["round_decimal"] = int(roundDecimal)
    #  Validate guarantee_timestamp and travel_timestamp
    if guarantee_timestamp:
        try:
            result["guarantee_timestamp"] = int(guarantee_timestamp)
        except Exception as e:
            raise ParameterException(
                'Format(int) "guarantee_timestamp" error! {}'.format(str(e))
            )
    if travel_timestamp:
        try:
            result["travel_timestamp"] = int(travel_timestamp)
        except Exception as e:
            raise ParameterException(
                'Format(int) "travel_timestamp" error! {}'.format(str(e))
            )
    return result


def validateQueryParams(expr, partitionNames, outputFields, timeout):
    result = {}
    if not expr:
        raise ParameterException("expr is empty!")
    # if ' in ' not in expr:
    if not any(map(lambda x: x in expr, Operators)):
        raise ParameterException(
            f'The query expression only accepts "<field_name> <oprator in {Operators}> [<value>, ...]"!'
        )
    result["expr"] = expr
    if not outputFields:
        result["output_fields"] = None
    else:
        nameList = outputFields.replace(" ", "").split(",")
        result["output_fields"] = nameList
    if not partitionNames:
        result["partition_names"] = None
    else:
        nameList = partitionNames.replace(" ", "").split(",")
        result["partition_names"] = nameList
    result["timeout"] = float(timeout) if timeout else None
    return result


def validateCalcParams(
    leftVectorMeta, rightVectorMeta, metric_type, sqrt, dim, timeout
):
    result = {"params": {}}
    vectors_left = validateVectorMeta(leftVectorMeta)
    result["vectors_left"] = vectors_left
    vectors_right = validateVectorMeta(rightVectorMeta)
    result["vectors_right"] = vectors_right
    params = result["params"]
    params["metric_type"] = metric_type
    if metric_type not in MetricTypes:
        raise ParameterException(
            "metric_type should be one of {}".format(str(MetricTypes))
        )
    if metric_type == "L2":
        params["sqrt"] = sqrt
    elif metric_type in ["HAMMING", "TANIMOTO"]:
        params["dim"] = dim
    if timeout:
        result["timeout"] = float(timeout)
    else:
        result["timeout"] = None
    return result


def validateVectorMeta(vectorMeta):
    import json

    vec_type = vectorMeta["vec_type"]
    result = {}
    if vec_type == "import":
        ids_str = vectorMeta["ids"]
        try:
            ids = json.loads(ids_str.replace("'", "").replace('"', ""))
        except Exception as e:
            raise ParameterException('Format(list[int]) "ids" error! {}'.format(str(e)))
        collection_str = vectorMeta["collection"]
        partition_str = vectorMeta["partition"]
        field_str = vectorMeta["field"]
        if not collection_str or not partition_str or not field_str:
            raise ParameterException("Collection/Partition/Field should not be empty!")
        result["ids"] = ids
        result["collection"] = collection_str
        result["partition"] = partition_str
        result["field"] = field_str
    if vec_type == "raw":
        vectors_str = vectorMeta["vectors"]
        if vectorMeta["type"] == "float_vectors":
            try:
                vectors = json.loads(vectors_str.replace("'", "").replace('"', ""))
            except Exception as e:
                raise ParameterException(
                    'Format(list[float]) "ids" error! {}'.format(str(e))
                )
            else:
                result[vectorMeta["type"]] = vectors
        elif vectorMeta["type"] == "bin_vectors":
            # """[b'\x94', b'N', b'\xca']"""
            noWhiteSpace = vectors_str.strip()
            noSquareBrackets = noWhiteSpace[1:-1]
            # "b'\x94', b'N', b'Ê'"
            strList = noSquareBrackets.split(", ")
            binMap = map(lambda x: x[2:-1].encode("unicode_escape"), strList)
            result[vectorMeta["type"]] = list(binMap)
    return result
