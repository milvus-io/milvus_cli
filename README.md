# milvus_cli🚀

- [milvus_cli🚀](#milvus_cli)
  - [Overview](#overview)
  - [Installation](#installation)
    - [Preparation](#preparation)
    - [Install from PYPI(recommend)](#install-from-pypirecommend)
    - [Install from release/source code](#install-from-releasesource-code)
  - [Usage](#usage)
    - [commands](#commands)
      - [`clear`](#clear)
      - [`connect`](#connect)
      - [`create`](#create)
        - [`create collection`](#create-collection)
        - [`create partition`](#create-partition)
        - [`create index`](#create-index)
      - [`delete`](#delete)
        - [`delete collection`](#delete-collection)
        - [`delete partition`](#delete-partition)
        - [`delete index`](#delete-index)
      - [`describe`](#describe)
        - [`describe collection`](#describe-collection)
        - [`describe partition`](#describe-partition)
      - [`exit`](#exit)
      - [`help`](#help)
      - [`import`](#import)
      - [`list`](#list)
        - [`list collections`](#list-collections)
        - [`list indexes`](#list-indexes)
        - [`list partitions`](#list-partitions)
      - [`load`](#load)
      - [`query` (prompt command)](#query-prompt-command)
      - [`release`](#release)
      - [`search` (prompt command)](#search-prompt-command)
      - [`show`](#show)
        - [`show connection`](#show-connection)
        - [`show index_progress`](#show-index_progress)
        - [`show loading_progress`](#show-loading_progress)
      - [`version`](#version)

## Overview

Milvus CLI based on [Milvus Python ORM SDK](https://github.com/milvus-io/pymilvus)


|Milvus version| Recommended PyMilvus version | Recommended CLI version |
|:-----:|:-----:|:-----:|
| 1.0.* | 1.0.1 | x |
| 1.1.* | 1.1.2 | x |
| 2.0.0-RC1 | 2.0.0rc1 | x |
| 2.0.0-RC2 | 2.0.0rc2 | 0.1.3 |
| 2.0.0-RC4 | 2.0.0rc4 | 0.1.4 |
| 2.0.0-RC5 | 2.0.0rc5 | 0.1.5 |
| 2.0.0-RC6 | 2.0.0rc6 | 0.1.6 |
| 2.0.0-RC7 | 2.0.0rc7 | 0.1.7 |

*\*It should be noted that Milvus 2.0.0-RC7 is NOT compatible with previous versions of Milvus 2.0.0 because of some changes made to storage format.*

## Installation

### Preparation

1. Install `Python` >= 3.8.5

2. Install `pip`

### Install from PYPI(recommend)

`pip install milvus-cli`

### Install from release/source code

1. Download [latest release](https://github.com/milvus-io/milvus_cli/releases/latest) or `git clone https://github.com/milvus-io/milvus_cli.git`
2. Enter the direction(`cd milvus_cli/`) and run `python -m pip install --editable .`

## Usage

Run `milvus_cli`

### commands

#### `clear`

```
milvus_cli > clear --help
Usage: milvus_cli.py clear [OPTIONS]

  Clear screen.

Options:
  --help  Show this message and exit.
```

#### `connect`

```
milvus_cli > connect --help
Usage: milvus_cli.py connect [OPTIONS]

  Connect to Milvus.

  Example:

      milvus_cli > connect -h 127.0.0.1 -p 19530 -a default

Options:
  -a, --alias TEXT    Milvus link alias name, default is `default`.
  -h, --host TEXT     Host name, default is `127.0.0.1`.
  -p, --port INTEGER  Port, default is `19530`.
  --help              Show this message and exit.
```

#### `create`

```
milvus_cli > create --help
Usage: milvus_cli.py create [OPTIONS] COMMAND [ARGS]...

  Create collection, partition and index.

Options:
  --help  Show this message and exit.

Commands:
  collection  Create partition.
  index       Create index.
  partition   Create partition.
```

##### `create collection`

```
milvus_cli > create collection --help
Usage: milvus_cli.py create collection [OPTIONS]

  Create partition.

  Example:

    create collection -c car -f id:INT64:primary_field -f vector:FLOAT_VECTOR:128 -f color:INT64:color -f brand:INT64:brand -p id -a -d 'car_collection'

Options:
  -c, --collection-name TEXT                 Collection name to be created.
  -p, --schema-primary-field TEXT
                                  Primary field name.
  -a, --schema-auto-id            Enable auto id.
  -d, --schema-description TEXT   Description details.
  -f, --schema-field TEXT         FieldSchema. Usage is
                                  "<Name>:<DataType>:<Dim(if vector) or
                                  Description>"
  --help                          Show this message and exit.
```

##### `create partition`

```
milvus_cli > create partition --help
Usage: milvus_cli.py create partition [OPTIONS]

  Create partition.

  Example:

      milvus_cli > create partition -c car -p new_partition -d test_add_partition

Options:
  -c, --collection TEXT   Collection name.
  -p, --partition TEXT    The name of partition.
  -d, --description TEXT  Partition description.
  --help                  Show this message and exit.
```

##### `create index`

```
milvus_cli > create index --help
Usage: milvus_cli.py create index [OPTIONS]

  Create index.

  Example:

      milvus_cli > create index

      Collection name (car, car2): car2

      The name of the field to create an index for (vector): vector

      Index type (FLAT, IVF_FLAT, IVF_SQ8, IVF_PQ, RNSG, HNSW, ANNOY):
      IVF_FLAT

      Index metric type (L2, IP, HAMMING, TANIMOTO): L2

      Index params nlist: 2

      Timeout []:

Options:
  --help  Show this message and exit.
```

#### `delete`

```
milvus_cli > delete --help
Usage: milvus_cli.py delete [OPTIONS] COMMAND [ARGS]...

  Delete specified collection, partition and index.

Options:
  --help  Show this message and exit.

Commands:
  collection  Drops the collection together with its index files.
  index       Drop index and its corresponding index files.
  partition   Drop the partition and its corresponding index files.
```

##### `delete collection`

```
milvus_cli > delete collection --help
Usage: milvus_cli.py delete collection [OPTIONS]

  Drops the collection together with its index files.

  Example:

      milvus_cli > delete collection -c car

Options:
  -c, --collection TEXT  The name of collection to be deleted.
  -t, --timeout INTEGER  An optional duration of time in seconds to allow for
                         the RPC. If timeout is set to None, the client keeps
                         waiting until the server responds or an error occurs.
  --help                 Show this message and exit.
```

##### `delete partition`

```
milvus_cli > delete partition --help
Usage: milvus_cli.py delete partition [OPTIONS]

  Drop the partition and its corresponding index files.

  Example:

      milvus_cli > delete partition -c car -p new_partition

Options:
  -c, --collection TEXT  Collection name
  -p, --partition TEXT   The name of partition.
  -t, --timeout INTEGER  An optional duration of time in seconds to allow for
                         the RPC. If timeout is set to None, the client keeps
                         waiting until the server responds or an error occurs.
  --help                 Show this message and exit.
```

##### `delete index`

```
milvus_cli > delete index --help
Usage: milvus_cli.py delete index [OPTIONS]

  Drop index and its corresponding index files.

  Example:

      milvus_cli > delete index -c car

Options:
  -c, --collection TEXT  Collection name
  -t, --timeout INTEGER  An optional duration of time in seconds to allow for
                         the RPC. If timeout is set to None, the client keeps
                         waiting until the server responds or an error occurs.
  --help                 Show this message and exit.
```

#### `describe`

```
milvus_cli > describe --help
Usage: milvus_cli.py describe [OPTIONS] COMMAND [ARGS]...

  Describe collection or partition.

Options:
  --help  Show this message and exit.

Commands:
  collection  Describe collection.
  partition   Describe partition.
```

##### `describe collection`

```
milvus_cli > describe collection --help
Usage: milvus_cli.py describe collection [OPTIONS]

  Describe collection.

  Example:

      milvus_cli > describe collection -c test_collection_insert

Options:
  -c, --collection TEXT  The name of collection.
  --help                 Show this message and exit.
```

##### `describe partition`

```
milvus_cli > describe partition --help
Usage: milvus_cli.py describe partition [OPTIONS]

  Describe partition.

  Example:

      milvus_cli > describe partition -c test_collection_insert -p _default

Options:
  -c, --collection TEXT  The name of collection.
  -p, --partition TEXT   The name of partition.
  --help                 Show this message and exit.
```

#### `exit`

```
milvus_cli > exit --help
Usage: milvus_cli.py exit [OPTIONS]

  Exit the CLI.

Options:
  --help  Show this message and exit.
```

#### `help`

```
milvus_cli > help
Usage:  [OPTIONS] COMMAND [ARGS]...

  Milvus CLI

Commands:
  clear     Clear screen.
  connect   Connect to Milvus.
  create    Create collection, partition and index.
  delete    Delete specified collection, partition and index.
  describe  Describe collection or partition.
  exit      Exit the CLI.
  help      Show help messages.
  import    Import data.
  list      List collections, partitions and indexes.
  load      Load specified collection.
  query     Query with a set of criteria, and results in a list of...
  release   Release specified collection.
  search    Conducts a vector similarity search with an optional boolean...
  show      Show connection, loading_progress and index_progress.
  version   Get Milvus CLI version.
```

#### `import`

```
milvus_cli > import --help
Usage: milvus_cli.py import [OPTIONS] PATH

  Import data.

  Example:

      milvus_cli > import 'examples/import_csv/vectors.csv' -c car

      Reading csv file...  [####################################]  100%

      Column names are ['vector', 'color', 'brand']

      Processed 50001 lines.

      Import successfully.

Options:
  -c, --collection TEXT  The name of collection to be imported.
  -p, --partition TEXT   The partition name which the data will be inserted
                         to, if partition name is not passed, then the data
                         will be inserted to “_default” partition.
  -t, --timeout FLOAT    An optional duration of time in seconds to allow for
                         the RPC. If timeout is set to None, the client keeps
                         waiting until the server responds or an error occurs.
  --help                 Show this message and exit.
```

#### `list`

```
milvus_cli > list --help
Usage: milvus_cli.py list [OPTIONS] COMMAND [ARGS]...

  List collections, partitions and indexes.

Options:
  --help  Show this message and exit.

Commands:
  collections  List all collections.
  indexes      List all indexes of the specified collection.
  partitions   List all partitions of the specified collection.
```

##### `list collections`

```
milvus_cli > list collections --help
Usage: milvus_cli.py list collections [OPTIONS]

  List all collections.

Options:
  --timeout TEXT         [Optional] - An optional duration of time in seconds
                         to allow for the RPC. When timeout is set to None,
                         client waits until server response or error occur.
  --show-loaded BOOLEAN  [Optional] - Only show loaded collections.
  --help                 Show this message and exit.
```

##### `list indexes`

```
milvus_cli > list indexes --help
Usage: milvus_cli.py list indexes [OPTIONS]

  List all indexes of the specified collection.

Options:
  -c, --collection TEXT  The name of collection.
  --help                 Show this message and exit.
```

##### `list partitions`

```
milvus_cli > list partitions --help
Usage: milvus_cli.py list partitions [OPTIONS]

  List all partitions of the specified collection.

Options:
  -c, --collection TEXT  The name of collection.
  --help                 Show this message and exit.
```

#### `load`

```
milvus_cli > load --help
Usage: milvus_cli.py load [OPTIONS]

  Load specified collection.

Options:
  -c, --collection TEXT  The name of collection to load.
  --help                 Show this message and exit.
```

#### `query` (prompt command)

```
milvus_cli > query --help
Usage: milvus_cli.py query [OPTIONS]

  Query with a set of criteria, and results in a list of records that match
  the query exactly.

  Example:

      milvus_cli > query

      Collection name: car

      The query expression(field_name in [x,y]): id in [ 427284660842954108, 427284660842954199 ]

      Name of partitions that contain entities(split by "," if multiple) []: default

      A list of fields to return(split by "," if multiple) []: color, brand

Options:
  --help  Show this message and exit.
```

#### `release`

```
milvus_cli > release --help
Usage: milvus_cli.py release [OPTIONS]

  Release specified collection.

Options:
  -c, --collection TEXT  The name of collection to be released.
  --help                 Show this message and exit.
```

#### `search` (prompt command)

```
milvus_cli > search --help
Usage: milvus_cli.py search [OPTIONS]

  Conducts a vector similarity search with an optional boolean expression as
  filter.

  Example-1(import a csv file):

      Collection name (car, test_collection): car

      The vectors of search data(the length of data is number of query (nq),
      the dim of every vector in data must be equal to vector field’s of
      collection. You can also import a csv file with out headers):
      examples/import_csv/search_vectors.csv

      The vector field used to search of collection (vector): vector

      Metric type: L2

      Search parameter nprobe's value: 10

      The max number of returned record, also known as topk: 2

      The boolean expression used to filter attribute []: id > 0

      The names of partitions to search(split by "," if multiple) ['_default']
      []: _default

  Example-2(collection has index):

      Collection name (car, test_collection): car

      The vectors of search data(the length of data is number of query (nq), 
      the dim of every vector in data must be equal to vector field’s of 
      collection. You can also import a csv file with out headers):
          [[0.71, 0.76, 0.17, 0.13, 0.42, 0.07, 0.15, 0.67, 0.58, 0.02, 0.39, 
          0.47, 0.58, 0.88, 0.73, 0.31, 0.23, 0.57, 0.33, 0.2, 0.03, 0.43, 
          0.78, 0.49, 0.17, 0.56, 0.76, 0.54, 0.45, 0.46, 0.05, 0.1, 0.43, 
          0.63, 0.29, 0.44, 0.65, 0.01, 0.35, 0.46, 0.66, 0.7, 0.88, 0.07, 
          0.49, 0.92, 0.57, 0.5, 0.16, 0.77, 0.98, 0.1, 0.44, 0.88, 0.82, 
          0.16, 0.67, 0.63, 0.57, 0.55, 0.95, 0.13, 0.64, 0.43, 0.71, 0.81, 
          0.43, 0.65, 0.76, 0.7, 0.05, 0.24, 0.03, 0.9, 0.46, 0.28, 0.92, 
          0.25, 0.97, 0.79, 0.73, 0.97, 0.49, 0.28, 0.64, 0.19, 0.23, 0.51, 
          0.09, 0.1, 0.53, 0.03, 0.23, 0.94, 0.87, 0.14, 0.42, 0.82, 0.91, 
          0.11, 0.91, 0.37, 0.26, 0.6, 0.89, 0.6, 0.32, 0.11, 0.98, 0.67, 
          0.12, 0.66, 0.47, 0.02, 0.15, 0.6, 0.64, 0.57, 0.14, 0.81, 0.75, 
          0.11, 0.49, 0.78, 0.16, 0.63, 0.57, 0.18]]

      The vector field used to search of collection (vector): vector

      Metric type: L2

      Search parameter nprobe's value: 10

      The specified number of decimal places of returned distance [-1]: 5

      The max number of returned record, also known as topk: 2

      The boolean expression used to filter attribute []: id > 0

      The names of partitions to search(split by "," if multiple) ['_default']
      []: _default

      timeout []:

  Example-3(collection has no index):

      Collection name (car, car2): car

      The vectors of search data(the length of data is number of query (nq),
      the dim of every vector in data must be equal to vector field’s of
      collection. You can also import a csv file with out headers):
      examples/import_csv/search_vectors.csv

      The vector field used to search of collection (vector): vector

      The specified number of decimal places of returned distance [-1]: 5

      The max number of returned record, also known as topk: 2

      The boolean expression used to filter attribute []:

      The names of partitions to search(split by "," if multiple) ['_default']
      []:

      Timeout []:

Options:
  --help  Show this message and exit.
```

#### `show`

```
milvus_cli > show --help
Usage: milvus_cli.py show [OPTIONS] COMMAND [ARGS]...

  Show connection, loading_progress and index_progress.

Options:
  --help  Show this message and exit.

Commands:
  connection        Show current/all connection details
  index_progress
  loading_progress  Show #loaded entities vs #total entities.
```

##### `show connection`

```
milvus_cli > show connection --help
Usage: milvus_cli.py show connection [OPTIONS]

  Show current/all connection details

Options:
  -a, --all  Show all connections.
  --help     Show this message and exit.
```

##### `show index_progress`

```
milvus_cli > show index_progress --help
Usage: milvus_cli.py show index_progress [OPTIONS]

Options:
  -c, --collection TEXT  The name of collection is loading
  -i, --index TEXT       [Optional] - Index name.
  --help                 Show this message and exit.
```

##### `show loading_progress`

```
milvus_cli > show loading_progress --help
Usage: milvus_cli.py show loading_progress [OPTIONS]

  Show #loaded entities vs #total entities.

Options:
  -c, --collection TEXT  The name of collection is loading
  -p, --partition TEXT   [Optional, Multiple] - The names of partitions are
                         loading
  --help                 Show this message and exit.
```

#### `version`

```
milvus_cli > --help
Usage: milvus_cli.py [OPTIONS] COMMAND [ARGS]...

  Milvus CLI

Options:
  --help  Show this message and exit.

Commands:
  clear     Clear screen.
  connect   Connect to Milvus.
  create    Create collection, partition and index.
  delete    Delete specified collection, partition and index.
  describe  Describe collection or partition.
  list      List collections, partitions and indexes.
  load      Load specified collection.
  query     Query with a set of criteria, and results in a list of...
  release   Release specified collection.
  search    Conducts a vector similarity search with an optional boolean...
  show      Show connection, loading_progress and index_progress.
  version   Get Milvus CLI version.
```

<br><!-- Do not remove start of hero-bot --><br>
<img src="https://img.shields.io/badge/all--contributors-3-orange"><br>
<a href="https://github.com/czhen-zilliz"><img src="https://avatars.githubusercontent.com/u/83751452?v=4" width="30px" /></a>
<a href="https://github.com/matrixji"><img src="https://avatars.githubusercontent.com/u/183388?v=4" width="30px" /></a>
<a href="https://github.com/sre-ci-robot"><img src="https://avatars.githubusercontent.com/u/56469371?v=4" width="30px" /></a>
<br><!-- Do not remove end of hero-bot --><br>
