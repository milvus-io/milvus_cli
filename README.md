# milvus_cli

[TOC]

## Installation

1. Install `Python` >= 3.8.5
2. Install `pip`
3. Download [latest release](https://github.com/milvus-io/milvus_cli/releases/latest) or `git clone https://github.com/milvus-io/milvus_cli.git`
4. Run `python -m pip install --editable .`

## Usage

Run `milvus_cli`

### commands

```
# milvus_cli commands:

connect    // Test the connection to Milvus with arguments `host`, `port` and `alias`.
           // Default values are `127.0.0.1`, `19530` and `default`.
           // All legal datas will be saved to a local tmp file `/tmp/.milvus_cli_test.yml`
    --host (str) – Host name, default is `127.0.0.1`.
    --port (int) – Port, default is `19530`.
    --alias (str) – Milvus link alias name, default is `default`.

version    // SDK version; milvus version(not support now)

show
    connection    // Show current/all connection details
        --all (flag) Show all connections.
    loading_progress    // Show loading progress for collection: loading_progress(collection_name, partition_names=None, using='default')
        --collection (str) – Collection name.
        --partition (str) – Partition name.
        --using (str) – Milvus link of create collection
    index_progress    // Show index progress for index: index_building_progress(collection_name, index_name='', using='default')
        --collection (str) – Collection name.
        --index (str) – Index name.
        --using (str) – Milvus link of create collection

load    // Load specified collection
    --collection (str) – Collection name.

list
    collections    // list all collections: pymilvus_orm.utility.list_collections(timeout=None, using='default') → list
        --timeout (float) – An optional duration of time in seconds to allow for the RPC. When timeout is set to None, client waits until server response or error occur.
        --using (str) – Milvus link of create collection
        --loaded (flag)   // only list loaded collection(not support now)
    partitions    // list all partitions for a collection: Collection.partitions
        --collection (str) – Collection name.
    indexes    // list all indexes: Collection.indexes
        --collection (str) – Collection name.

describe
    collection    // describe collection: Collection.description; has_collection(name)
        <collectionName>
    partition    // describe partition: Partition.description; has_partition(collection_name, partition_name, using='default')
        --collection (str) – Collection name.
        <partitionName>

create
    collection    // create collection: Collection(name, schema=None, using='default', **kwargs)
        --name (str) – Collection name.
        --schema
            -fields*
            -primary_field (str) – Primary field name.
            -auto_id (flag) (bool) Enable auto id.
            -description (str) – Description details.
    partition    // create partition in a collection: Partition(collection, name, description='', **kwargs)
        --collection (str) – Collection name.
        --name (str) – Partition name.
        --description (str) – Description details.
    index    // create an index: Index(collection, field_name, index_params)
        --collection (str) – Collection name.
        --field (str) – Field name.
        --index        // index_params
            -index-type (str) - Index type name.
            -params**
            -metric-type (str) - Metric type name.


delete
    collection    // collection.drop(**kwargs)
        --collection (str) – Collection name.
        --timeout(optional) (float) – An optional duration of time in seconds to allow for the RPC. When timeout is set to None, client waits until server response or error occur.
    partition    // collection.drop_partition("new_partition")
        --collection  (str) – Collection name.
        --name   (str) – Partition name.
    index    // Index(collection, field_name, index_params, **kwargs)
             // add index_progress
      --collection  (str) – Collection name.

    
search // do vector search: Collection.search(data, anns_field, param, limit, expr=None, partition_names=None, output_fields=None, timeout=None, **kwargs)
    --collection (str) – Collection name.
    --data (list[list[float]]) – The vectors of search data, the length of data is number of query (nq), the dim of every vector in data must be equal to vector field’s of collection.
    --anns_field (str) – The vector field used to search of collection.
    --param (dict) – The parameters of search, such as nprobe.
    --limit (int) – The max number of returned record, also known as topk.
    --expr (str) – The boolean expression used to filter attribute.
    --partition_names (list[str]) – The names of partitions to search.
    --output_fields (list[str]) – A list of fields to return(not support now)
    --timeout (float) – An optional duration of time in seconds to allow for the RPC. When timeout is set to None, client waits until server response or error occur.

query // query entities: Collection.query(expr, output_fields=None, partition_names=None, timeout=None)
    --collection (str) – Collection name.
    --expr (str) – The query expression
    --output_fields (list[str]) – A list of fields to return
    --partition_names (list[str]) – Name of partitions that contain entities
    --timeout (float) – An optional duration of time in seconds to allow for the RPC. When timeout is set to None, client waits until server response or error occur.

import (on going)
    <fileName: xxx.csv >    // import file xxx.csv
    --collection (str) – Collection name.
    --partition (str) – Partition name.



---------
*
fields contains of FieldSchema, usage looks like below:
FieldSchema(name="id", dtype=DataType.INT64,  description="primary_field")
FieldSchema(name="year", dtype=DataType.INT64, description="year")
FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim)
--fields id:int64:primary_field  year:int64:year embedding:FLOAT_VECTOR:128

**
index = {"index_type": "IVF_FLAT", "params": {"nlist": 128}, "metric_type": "L2"}
collection.create_index("films", index)
--index-params nlist:128
```