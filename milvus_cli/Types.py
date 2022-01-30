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
    "FLOAT_VECTOR",
]

IndexTypes = [
    "FLAT",
    "IVF_FLAT",
    "IVF_SQ8",
    "IVF_PQ",
    "RNSG",
    "HNSW",
    # "NSG",
    "ANNOY",
    # "RHNSW_FLAT",
    # "RHNSW_PQ",
    # "RHNSW_SQ",
    # "BIN_FLAT",
    # "BIN_IVF_FLAT"
]

IndexParams = [
    "nlist",
    "m",
    "nbits",
    "M",
    "efConstruction",
    "n_trees",
    "PQM",
]

IndexTypesMap = {
    "FLAT": {
        "index_building_parameters": [],
        "search_parameters": ["metric_type"],
    },
    "IVF_FLAT": {
        "index_building_parameters": ["nlist"],
        "search_parameters": ["nprobe"],
    },
    "IVF_SQ8": {
        "index_building_parameters": ["nlist"],
        "search_parameters": ["nprobe"],
    },
    "IVF_PQ": {
        "index_building_parameters": ["nlist", "m", "nbits"],
        "search_parameters": ["nprobe"],
    },
    "RNSG": {
        "index_building_parameters": [
            "out_degree",
            "candidate_pool_size",
            "search_length",
            "knng",
        ],
        "search_parameters": ["search_length"],
    },
    "HNSW": {
        "index_building_parameters": ["M", "efConstruction"],
        "search_parameters": ["ef"],
    },
    "ANNOY": {
        "index_building_parameters": ["n_trees"],
        "search_parameters": ["search_k"],
    },
}

SearchParams = {search_param for index_params in IndexTypesMap.values() for search_param in index_params["search_parameters"]}

MetricTypes = ["L2", "IP", "HAMMING", "TANIMOTO"]

DataTypeByNum = {
    0: "NONE",
    1: "BOOL",
    2: "INT8",
    3: "INT16",
    4: "INT32",
    5: "INT64",
    10: "FLOAT",
    11: "DOUBLE",
    20: "STRING",
    100: "BINARY_VECTOR",
    101: "FLOAT_VECTOR",
    999: "UNKNOWN",
}

Operators = ["<", "<=", ">", ">=", "==", "!=", "in"]
