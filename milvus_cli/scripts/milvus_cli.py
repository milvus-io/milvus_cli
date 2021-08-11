from pymilvus_orm import connections
from tabulate import tabulate
import sys
import os
import click
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from utils import ParameterException, validateCollectionParameter, validateIndexParameter


class PyOrm(object):
    host = '127.0.0.1'
    port = 19530
    alias = 'default'

    def connect(self, alias=None, host=None, port=None):
        self.alias = alias
        self.host = host
        self.port = port
        # from pymilvus_orm import connections
        connections.connect(self.alias, host=self.host, port=self.port)

    def showConnection(self, alias, showAll=False):
        from pymilvus_orm import connections
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

    def listCollections(self, timeout=None, using="default", showLoadedOnly=False):
        from pymilvus_orm import list_collections
        result = []
        collectionNames = list_collections(timeout, using)
        for name in collectionNames:
            loadingProgress = self.showCollectionLoadingProgress(name)
            loaded, total = loadingProgress.values()
            isLoaded = (total > 0) and (loaded == total)
            shouldBeAdded = isLoaded if showLoadedOnly else True
            if shouldBeAdded:
                result.append([name, isLoaded, "{}/{}".format(loaded, total)])
        return tabulate(result, headers=['Collection Name', 'Loaded', 'Entities(Loaded/Total)'], tablefmt='grid', showindex=True)

    def showCollectionLoadingProgress(self, collectionName, partition_names=None, using='default'):
        from pymilvus_orm import loading_progress
        return loading_progress(collectionName, partition_names, using)

    def showIndexBuildingProgress(self, collectionName, index_name="", using="default"):
        from pymilvus_orm import index_building_progress
        return index_building_progress(collectionName, index_name, using)

    def getTargetCollection(self, collectionName):
        from pymilvus_orm import Collection
        return Collection(collectionName)

    def loadCollection(self, collectionName):
        target = self.getTargetCollection(collectionName)
        target.load()
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
        fieldSchemaDetails = "\n  - " + "\n  - ".join(map(lambda x: "{} *primary".format(
            x.name) if x.is_primary else x.name, schema.fields))
        schemaDetails = """Description: {}\nFields:{}""".format(
            schema.description, fieldSchemaDetails)
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
        from pymilvus_orm import Collection, DataType, FieldSchema, CollectionSchema
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
        index = {"index_type": indexType, "params": indexParams, "metric_type": metricType}
        collection.create_index(fieldName, index, timeout=timeout)
        return self.getIndexDetails(collection)
    
    def isCollectionExist(self, collectionName):
        from pymilvus_orm import has_collection
        return has_collection(collectionName, using=self.alias)

    def dropCollection(self, collectionName, timeout):
        collection = self.getTargetCollection(collectionName)
        collection.drop(timeout=timeout)
        return self.isCollectionExist(collectionName)


pass_context = click.make_pass_decorator(PyOrm, ensure=True)


@click.group()
@click.pass_context
def cli(ctx):
    """Milvus CLI"""
    ctx.obj = PyOrm()


@cli.command()
@click.option('--alias', 'alias', help="[Optional] - Milvus link alias name, default is `default`.", default='default', type=str)
@click.option('--host', 'host', help="[Optional] - Host name, default is `127.0.0.1`.", default='127.0.0.1', type=str)
@click.option('--port', 'port', help="[Optional] - Port, default is `19530`.", default=19530, type=int)
@click.pass_obj
def connect(obj, alias, host, port):
    """Connect to Milvus"""
    try:
        obj.connect(alias, host, port)
    except Exception as e:
        click.echo(message=e, err=True)
    else:
        click.echo("Connect Milvus successfully!")
        click.echo(obj.showConnection(alias))


@cli.command()
def version():
    """Get Milvus CLI version."""
    click.echo("SDK version: {}".format("0.0.alpha"))


@cli.group()
@click.pass_obj
def show(obj):
    """Show connection, loading_progress and index_progress."""
    pass


@show.command()
@click.option('--all', 'showAll', help="[Optional] - Show all connections.", default=False, is_flag=True)
@click.pass_obj
def connection(obj, showAll):
    """Show current/all connection details"""
    click.echo(obj.showConnection('default', showAll))


@show.command('loading_progress')
@click.option('-c', '--collection', 'collection', help='The name of collection is loading', default='')
@click.option('-p', '--partition', 'partition', help='[Optional, Multiple] - The names of partitions are loading', default=None, multiple=True)
@click.option('-u', '--using', 'using', help='[Optional] - Milvus link of create collection', default='default')
@click.pass_obj
def loadingProgress(obj, collection, partition, using):
    """Show #loaded entities vs #total entities."""
    result = obj.showCollectionLoadingProgress(collection, partition, using)
    click.echo(tabulate([[result.get('num_loaded_entities'), result.get('num_total_entities')]], headers=[
               'num_loaded_entities', 'num_total_entities'], tablefmt='pretty'))


@show.command('index_progress')
@click.option('-c', '--collection', 'collection', help='The name of collection is loading', default='')
@click.option('-i', '--index', 'index', help='[Optional] - Index name.', default='')
@click.option('-u', '--using', 'using', help='[Optional] - Milvus link of create collection.', default='default')
@click.pass_obj
def indexProgress(obj, collection, index, using):
    result = obj.showIndexBuildingProgress(collection, index, using)
    click.echo(tabulate([[result.get('indexed_rows'), result.get('total_rows')]], headers=[
               'indexed_rows', 'total_rows'], tablefmt='pretty'))


@cli.command()
@click.option('-c', '--collection', 'collection', help='The name of collection to load.', default='')
@click.pass_obj
def load(obj, collection):
    """Load specified collection."""
    try:
        result = obj.loadCollection(collection)
    except Exception as e:
        click.echo(message=e, err=True)
    else:
        click.echo("""Load Collection '{}' successfully""".format(collection))
        click.echo(result)


@cli.group('list')
@click.pass_obj
def listDetails(obj):
    """List collections, partitions and indexes."""
    pass


@listDetails.command()
@click.option('--timeout', 'timeout', help="[Optional] - An optional duration of time in seconds to allow for the RPC. When timeout is set to None, client waits until server response or error occur.", default=None)
@click.option('--using', 'using', help="[Optional] - Milvus link of create collection.", default='default')
@click.option('--show-loaded', 'showLoaded', help="[Optional] - Only show loaded collections.", default=False)
@click.pass_obj
def collections(obj, timeout, using, showLoaded):
    """List all collections."""
    click.echo(obj.listCollections(timeout, using, showLoaded))


@listDetails.command()
@click.option('-c', '--collection', 'collection', help='The name of collection.', default='')
@click.pass_obj
def partitions(obj, collection):
    """List all partitions of the specified collection."""
    click.echo(obj.listPartitions(collection))


@listDetails.command()
@click.option('-c', '--collection', 'collection', help='The name of collection.', default='')
@click.pass_obj
def indexes(obj, collection):
    """List all indexes of the specified collection."""
    click.echo(obj.listIndexes(collection))


@cli.group('describe')
@click.pass_obj
def describeDetails(obj):
    """Describe collection or partition."""
    pass


@describeDetails.command('collection')
@click.argument('collection')
@click.pass_obj
def describeCollection(obj, collection):
    """Describe collection."""
    click.echo(obj.getCollectionDetails(collection))


@describeDetails.command('partition')
@click.option('-c', '--collection', 'collectionName', help='The name of collection.', default='')
@click.argument('partition')
@click.pass_obj
def describePartition(obj, collectionName, partition):
    """Describe partition."""
    try:
        collection = obj.getTargetCollection(collectionName)
    except Exception as e:
        click.echo("Error when get collection!")
    else:
        click.echo(obj.getPartitionDetails(collection, partition))


@cli.group('create')
@click.pass_obj
def createDetails(obj):
    """Create collection, partition and index."""
    pass


@createDetails.command('collection')
@click.option('-n', '--name', 'collectionName', help='Collection name to be created.', default='')
@click.option('-p', '--schema-primary-field', 'primaryField', help='Primary field name.', default='')
@click.option('-a', '--schema-auto-id', 'autoId', help='Enable auto id.', default=False, is_flag=True)
@click.option('-d', '--schema-description', 'description', help='Description details.', default='')
@click.option('-f', '--schema-field', 'fields', help='FieldSchema. Usage is "<Name>:<DataType>:<Dim(if vector) or Description>"', default=None, multiple=True)
@click.pass_obj
def createCollection(obj, collectionName, primaryField, autoId, description, fields):
    """
    Create partition.

    Example:

      create collection -n tutorial -f id:INT64:primary_field -f year:INT64:year -f embedding:FLOAT_VECTOR:128 -p id -d 'desc of collection'
    """
    try:
        validateCollectionParameter(
            collectionName, primaryField, fields)
    except ParameterException as e:
        click.echo("Error!\n{}".format(str(e)))
    else:
        click.echo(obj.createCollection(collectionName,
                   primaryField, autoId, description, fields))
        click.echo("Create collection successfully!")


@createDetails.command('partition')
@click.option('-c', '--collection', 'collectionName', help='Collection name.', default='')
@click.option('-d', '--description', 'description', help='Partition description.', default='')
@click.argument('partition')
@click.pass_obj
def createPartition(obj, collectionName, description, partition):
    """
    Create partition.
    """
    try:
        obj.getTargetCollection(collectionName)
    except Exception as e:
        click.echo("Error occurred when get collection by name!")
    else:
        click.echo(obj.createPartition(collectionName, description, partition))
        click.echo("Create partition successfully!")


@createDetails.command('index')
@click.option('-c', '--collection', 'collectionName', help='Collection name.', default='')
@click.option('-f', '--field', 'fieldName', help='The name of the field to create an index for.', default='')
@click.option('-t', '--index-type', 'indexType', help='Index type.', default='')
@click.option('-m', '--index-metric', 'metricType', help='Index metric type.', default='')
@click.option('-p', '--index-params', 'params', help='Index params, usage is "<Name>:<Value>"', default=None, multiple=True)
@click.option('-e', '--timeout', 'timeout', help='An optional duration of time in seconds to allow for the RPC. When timeout is set to None, client waits until server response or error occur.', default=None, type=int)
@click.pass_obj
def createIndex(obj, collectionName, fieldName, indexType, metricType, params, timeout):
    """
    Create index.

    Example:

      create index -n film -f films -t IVF_FLAT -m L2 -p nlist:128
    """
    try:
        validateIndexParameter(
            indexType, metricType, params)
    except ParameterException as e:
        click.echo("Error!\n{}".format(str(e)))
    else:
        click.echo(obj.createIndex(collectionName, fieldName, indexType, metricType, params, timeout))
        click.echo("Create index successfully!")


@cli.group('delete')
@click.pass_obj
def deleteObject(obj):
    """Delete specified collection, partition and index."""
    pass


@deleteObject.command('collection')
@click.option('-t', '--timeout', 'timeout', help='An optional duration of time in seconds to allow for the RPC. If timeout is set to None, the client keeps waiting until the server responds or an error occurs.', default=None, type=int)
@click.option('-y', 'deleteCheck', help='Delete check.', default=False, is_flag=True)
@click.argument('collection')
@click.pass_obj
def createPartition(obj, timeout, deleteCheck, collection):
    """
    Drop collection.
    """
    click.echo("You are trying to delete the collection with data. This action cannot be undone!")
    if not deleteCheck:
        return click.echo("Use '-y' if you are sure to delete the collection {}.".format(collection))
    try:
        obj.getTargetCollection(collection)
    except Exception as e:
        click.echo("Error occurred when get collection by name!")
    else:
        result = obj.dropCollection(collection, timeout)
        click.echo("Drop collection successfully!") if not result else click.echo("Drop collection failed!")


if __name__ == '__main__':
    while True:
        astr = input('milvus_cli > ')
        try:
            # print('astr===> ', astr)
            cli(astr.split())
        except SystemExit:
            # trap argparse error message
            # print('error', SystemExit)
            continue
