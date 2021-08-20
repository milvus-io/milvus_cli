# milvus_cli

- [milvus_cli](#milvus-cli)
  * [Overview](#overview)
  * [Installation](#installation)
  * [Usage](#usage)
    + [commands](#commands)
      - [`connect`](#connect)
      - [`clear`](#clear)
      - [`connect`](#connect-1)
      - [`create`](#create)
        * [`create collection`](#create-collection)
        * [`create partition`](#create-partition)
        * [`create index`](#create-index)
      - [`delete`](#delete)
        * [`delete collection`](#delete-collection)
        * [`delete partition`](#delete-partition)
        * [`delete index`](#delete-index)
      - [`describe`](#describe)
        * [`describe collection`](#describe-collection)
        * [`describe partition`](#describe-partition)
      - [`list`](#list)
        * [`list collections`](#list-collections)
        * [`list indexes`](#list-indexes)
        * [`list partitions`](#list-partitions)
      - [`load`](#load)
      - [`query` (prompt command)](#-query-prompt-command)
      - [`release`](#release)
      - [`search`(prompt command)](#-search-prompt-command)
      - [`show`](#show)
        * [`show connection`](#show-connection)
        * [`show index_progress`](#show-index-progress)
        * [`show loading_progress`](#show-loading-progress)
      - [`version`](#version)

## Overview

Milvus CLI based on [Milvus Python ORM SDK](https://github.com/milvus-io/pymilvus)


|Milvus version| Recommended PyMilvus version | Recommended CLI version |
|:-----:|:-----:|:-----:|
| 1.0.* | 1.0.1 | x |
| 1.1.* | 1.1.2 | x |
| 2.0.0-RC1 | 2.0.0rc1 | x |
| 2.0.0-RC2 | 2.0.0rc2 | 0.1.3 |
| 2.0.0-RC4 | 2.0.0rc4 |  |

## Installation

1. Install `Python` >= 3.8.5
2. Install `pip`
3. Download [latest release](https://github.com/milvus-io/milvus_cli/releases/latest) or `git clone https://github.com/milvus-io/milvus_cli.git`
4. Run `python -m pip install --editable .`

## Usage

Run `milvus_cli`

### commands

#### `connect`

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

    create collection -n tutorial -f id:INT64:primary_field -f year:INT64:year
    -f embedding:FLOAT_VECTOR:128 -p id -d 'desc of collection'

Options:
  -n, --name TEXT                 Collection name to be created.
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
Usage: milvus_cli.py create partition [OPTIONS] PARTITION

  Create partition.

Options:
  -c, --collection TEXT   Collection name.
  -d, --description TEXT  Partition description.
  --help                  Show this message and exit.
```

##### `create index`

```
milvus_cli > create index --help
Usage: milvus_cli.py create index [OPTIONS]

  Create index.

  Example:

    create index -n film -f films -t IVF_FLAT -m L2 -p nlist:128

Options:
  -c, --collection TEXT    Collection name.
  -f, --field TEXT         The name of the field to create an index for.
  -t, --index-type TEXT    Index type.
  -m, --index-metric TEXT  Index metric type.
  -p, --index-params TEXT  Index params, usage is "<Name>:<Value>"
  -e, --timeout INTEGER    An optional duration of time in seconds to allow
                           for the RPC. When timeout is set to None, client
                           waits until server response or error occur.
  --help                   Show this message and exit.
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
Usage: milvus_cli.py delete collection [OPTIONS] COLLECTION

  Drops the collection together with its index files.

Options:
  -t, --timeout INTEGER  An optional duration of time in seconds to allow for
                         the RPC. If timeout is set to None, the client keeps
                         waiting until the server responds or an error occurs.
  --help                 Show this message and exit.
```

##### `delete partition`

```
milvus_cli > delete partition --help
Usage: milvus_cli.py delete partition [OPTIONS] PARTITION

  Drop the partition and its corresponding index files.

Options:
  -c, --collection TEXT  Collection name
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
Usage: milvus_cli.py describe collection [OPTIONS] COLLECTION

  Describe collection.

Options:
  --help  Show this message and exit.
```

##### `describe partition`

```
milvus_cli > describe partition --help
Usage: milvus_cli.py describe partition [OPTIONS] PARTITION

  Describe partition.

Options:
  -c, --collection TEXT  The name of collection.
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

      Collection name: test_collection_query

      The query expression: film_id in [ 0, 1 ]

      Name of partitions that contain entities(split by "," if multiple) []:

      A list of fields to return(split by "," if multiple) []: film_date

      timeout []:

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

  Example:

      Collection name: test_collection_search

      The vectors of search data, the length of data is number of query (nq),
      the dim of every vector in data must be equal to vector field’s of
      collection: [[1.0, 1.0]]

      The vector field used to search of collection []: films

      Metric type []: L2

      The parameters of search(split by "," if multiple) []:

      The max number of returned record, also known as topk []: 2

      The boolean expression used to filter attribute []: film_id > 0

      The names of partitions to search(split by "," if multiple) []:

      timeout []:

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

