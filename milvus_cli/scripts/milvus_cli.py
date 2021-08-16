from tabulate import tabulate
import sys
import os
import click
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from utils import PyOrm, getPackageVersion, ParameterException, validateCollectionParameter, validateIndexParameter, validateSearchParams, validateQueryParams


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
    """Connect to Milvus."""
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
    click.echo(f"Milvus Cli v{getPackageVersion()}")


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
# @click.option('-u', '--using', 'using', help='[Optional] - Milvus link of create collection', default='default')
@click.pass_obj
def loadingProgress(obj, collection, partition):
    """Show #loaded entities vs #total entities."""
    result = obj.showCollectionLoadingProgress(collection, partition)
    click.echo(tabulate([[result.get('num_loaded_entities'), result.get('num_total_entities')]], headers=[
               'num_loaded_entities', 'num_total_entities'], tablefmt='pretty'))


@show.command('index_progress')
@click.option('-c', '--collection', 'collection', help='The name of collection is loading', default='')
@click.option('-i', '--index', 'index', help='[Optional] - Index name.', default='')
# @click.option('-u', '--using', 'using', help='[Optional] - Milvus link of create collection.', default='default')
@click.pass_obj
def indexProgress(obj, collection, index):
    result = obj.showIndexBuildingProgress(collection, index)
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
# @click.option('--using', 'using', help="[Optional] - Milvus link of create collection.", default='default')
@click.option('--show-loaded', 'showLoaded', help="[Optional] - Only show loaded collections.", default=False)
@click.pass_obj
def collections(obj, timeout, showLoaded):
    """List all collections."""
    click.echo(obj.listCollections(timeout, showLoaded))


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
@click.argument('collection')
@click.pass_obj
def deleteCollection(obj, timeout, collection):
    """
    Drops the collection together with its index files.
    """
    click.echo("Warning!\nYou are trying to delete the collection with data. This action cannot be undone!\n")
    if not click.confirm('Do you want to continue?'):
        return
    try:
        obj.getTargetCollection(collection)
    except Exception as e:
        click.echo("Error occurred when get collection by name!")
    else:
        result = obj.dropCollection(collection, timeout)
        click.echo("Drop collection successfully!") if not result else click.echo("Drop collection failed!")


@deleteObject.command('partition')
@click.option('-c', '--collection', 'collectionName', help='Collection name', default=None)
@click.option('-t', '--timeout', 'timeout', help='An optional duration of time in seconds to allow for the RPC. If timeout is set to None, the client keeps waiting until the server responds or an error occurs.', default=None, type=int)
@click.argument('partition')
@click.pass_obj
def deletePartition(obj, collectionName, timeout, partition):
    """
    Drop the partition and its corresponding index files.
    """
    click.echo("Warning!\nYou are trying to delete the partition with data. This action cannot be undone!\n")
    if not click.confirm('Do you want to continue?'):
        return
    try:
        obj.getTargetCollection(collectionName)
    except Exception as e:
        click.echo("Error occurred when get collection by name!")
    else:
        result = obj.dropPartition(collectionName, partition, timeout)
        click.echo("Drop partition successfully!") if not result else click.echo("Drop partition failed!")


@deleteObject.command('index')
@click.option('-c', '--collection', 'collectionName', help='Collection name', default=None)
@click.option('-t', '--timeout', 'timeout', help='An optional duration of time in seconds to allow for the RPC. If timeout is set to None, the client keeps waiting until the server responds or an error occurs.', default=None, type=int)
@click.pass_obj
def deleteIndex(obj, collectionName, timeout):
    """
    Drop index and its corresponding index files.
    """
    click.echo("Warning!\nYou are trying to delete the index of collection. This action cannot be undone!\n")
    if not click.confirm('Do you want to continue?'):
        return
    try:
        obj.getTargetCollection(collectionName)
    except Exception as e:
        click.echo("Error occurred when get collection by name!")
    else:
        result = obj.dropIndex(collectionName, timeout)
        click.echo("Drop index successfully!") if not result else click.echo("Drop index failed!")


@cli.command()
# @click.option('-c', '--collection', 'collectionName', help='Collection name.', default=None)
# @click.option('-d', '--data', 'data', help='The vectors of search data, the length of data is number of query (nq), the dim of every vector in data must be equal to vector field’s of collection.', default=None)
# @click.option('-a', '--anns_field', 'annsField', help='The vector field used to search of collection.', default=None)
# @click.option('-m', '--metric_type', 'metricType', help='The parameters of search.', default=None)
# @click.option('-p', '--params', 'params', help='The parameters of search.', default=None, multiple=True)
# @click.option('-l', '--limit', 'limit', help='The max number of returned record, also known as topk.', default=None, type=int)
# @click.option('-e', '--expr', 'expr', help='The boolean expression used to filter attribute.', default=None)
# @click.option('-n', '--partition_names', 'partitionNames', help='The names of partitions to search.', default=None, multiple=True)
# # @click.option('-c', '--output_fields', 'collectionName', help='The fields to return in the search result, not supported now.', default=None)
# @click.option('-t', '--timeout', 'timeout', help='An optional duration of time in seconds to allow for the RPC. When timeout is set to None, client waits until server response or error occur.', default=None, type=float)
@click.pass_obj
# def search(obj, collectionName, data, annsField, metricType, params, limit, expr, partitionNames, timeout):
def search(obj):
    """
    Conducts a vector similarity search with an optional boolean expression as filter.

    Example:
        search -c test_collection_search -d '[[1.0,1.0]]' -a films -m L2 -l 2 -e film_id>0
    """
    collectionName = click.prompt('Collection name')
    data = click.prompt('The vectors of search data, the length of data is number of query (nq), the dim of every vector in data must be equal to vector field’s of collection')
    annsField = click.prompt('The vector field used to search of collection', default='')
    metricType = click.prompt('Metric type', default='')
    params = click.prompt('The parameters of search(split by "," if multiple)', default='')
    limit = click.prompt('The max number of returned record, also known as topk', default='')
    expr = click.prompt('The boolean expression used to filter attribute', default='')
    partitionNames = click.prompt('The names of partitions to search(split by "," if multiple)', default='')
    timeout = click.prompt('timeout', default='')
    try:
        searchParameters = validateSearchParams(data, annsField, metricType, params, limit, expr, partitionNames, timeout)
    except ParameterException as e:
        click.echo("Error!\n{}".format(str(e)))
    else:
        click.echo(obj.search(collectionName, searchParameters))


@cli.command()
@click.pass_obj
def query(obj):
    """
    Query with a set of criteria, and results in a list of records that match the query exactly.

    Example:

        milvus_cli > query

        Collection name: test_collection_query

        The query expression: film_id in [ 0, 1 ]

        Name of partitions that contain entities(split by "," if multiple) []: 

        A list of fields to return(split by "," if multiple) []: film_date

        timeout []: 
    """
    collectionName = click.prompt('Collection name')
    expr = click.prompt('The query expression')
    partitionNames = click.prompt('Name of partitions that contain entities(split by "," if multiple)', default='')
    outputFields = click.prompt('A list of fields to return(split by "," if multiple)', default='')
    timeout = click.prompt('timeout', default='')
    try:
        queryParameters = validateQueryParams(expr, partitionNames, outputFields, timeout)
    except ParameterException as e:
        click.echo("Error!\n{}".format(str(e)))
    else:
        click.echo(obj.query(collectionName, queryParameters))


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
