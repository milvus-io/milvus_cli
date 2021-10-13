from tabulate import tabulate
import sys
import os
import click
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from utils import PyOrm, Completer, getPackageVersion
from Fs import readCsvFile
from Validation import validateParamsByCustomFunc, validateCollectionParameter, validateIndexParameter, validateSearchParams, validateQueryParams
from Types import ParameterException, ConnectException
from Types import MetricTypes, IndexTypesMap, IndexTypes


pass_context = click.make_pass_decorator(PyOrm, ensure=True)


@click.group(no_args_is_help=False, add_help_option=False, invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Milvus CLI"""
    ctx.obj = PyOrm()


def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


@cli.command()
def help():
    """Show help messages."""
    click.echo(print_help_msg(cli))


@cli.command(no_args_is_help=False)
@click.option('-a', '--alias', 'alias', help="Milvus link alias name, default is `default`.", default='default', type=str)
@click.option('-h', '--host', 'host', help="Host name, default is `127.0.0.1`.", default='127.0.0.1', type=str)
@click.option('-p', '--port', 'port', help="Port, default is `19530`.", default=19530, type=int)
@click.pass_obj
def connect(obj, alias, host, port):
    """
    Connect to Milvus.

    Example:

        milvus_cli > connect -h 127.0.0.1 -p 19530 -a default
    """
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


@cli.command()
def clear():
    """Clear screen."""
    click.clear()


@cli.group(no_args_is_help=False)
@click.pass_obj
def show(obj):
    """Show connection, loading_progress and index_progress."""
    pass


@show.command()
@click.option('-a', '--all', 'showAll', help="Show all connections.", default=False, is_flag=True)
@click.pass_obj
def connection(obj, showAll):
    """Show current/all connection details"""
    obj.checkConnection()
    click.echo(obj.showConnection(showAll=showAll))


@show.command('loading_progress')
@click.option('-c', '--collection', 'collection', help='The name of collection is loading')
@click.option('-p', '--partition', 'partition', help='[Optional, Multiple] - The names of partitions are loading', default=None, multiple=True)
@click.pass_obj
def loadingProgress(obj, collection, partition):
    """Show #loaded entities vs #total entities."""
    try:
        obj.checkConnection()
        validateParamsByCustomFunc(
            obj.getTargetCollection, 'Collection Name Error!', collection)
        result = obj.showCollectionLoadingProgress(collection, partition)
    except Exception as e:
        click.echo(message=e, err=True)
    else:
        click.echo(tabulate([[result.get('num_loaded_entities'), result.get('num_total_entities')]], headers=[
            'num_loaded_entities', 'num_total_entities'], tablefmt='pretty'))


@show.command('index_progress')
@click.option('-c', '--collection', 'collection', help='The name of collection is loading', default='')
@click.option('-i', '--index', 'index', help='[Optional] - Index name.', default='')
@click.pass_obj
def indexProgress(obj, collection, index):
    """Show # indexed entities vs. # total entities."""
    try:
        obj.checkConnection()
        validateParamsByCustomFunc(
            obj.getTargetCollection, 'Collection Name Error!', collection)
        result = obj.showIndexBuildingProgress(collection, index)
    except Exception as e:
        click.echo(message=e, err=True)
    else:
        click.echo(tabulate([[result.get('indexed_rows'), result.get('total_rows')]], headers=[
            'indexed_rows', 'total_rows'], tablefmt='pretty'))


@cli.command()
@click.option('-c', '--collection', 'collection', help='The name of collection to load.', default='')
@click.pass_obj
def load(obj, collection):
    """Load specified collection."""
    try:
        validateParamsByCustomFunc(
            obj.getTargetCollection, 'Collection Name Error!', collection)
        result = obj.loadCollection(collection)
    except Exception as e:
        click.echo(message=e, err=True)
    else:
        click.echo("""Load Collection '{}' successfully""".format(collection))
        click.echo(result)


@cli.command()
@click.option('-c', '--collection', 'collection', help='The name of collection to be released.')
@click.pass_obj
def release(obj, collection):
    """Release specified collection."""
    try:
        validateParamsByCustomFunc(
            obj.getTargetCollection, 'Collection Name Error!', collection)
        result = obj.releaseCollection(collection)
    except Exception as e:
        click.echo(message=e, err=True)
    else:
        click.echo("""Release Collection '{}' successfully""".format(collection))
        click.echo(result)


@cli.group('list', no_args_is_help=False)
@click.pass_obj
def listDetails(obj):
    """List collections, partitions and indexes."""
    pass


@listDetails.command()
@click.option('--timeout', 'timeout', help="[Optional] - An optional duration of time in seconds to allow for the RPC. When timeout is set to None, client waits until server response or error occur.", default=None)
@click.option('--show-loaded', 'showLoaded', help="[Optional] - Only show loaded collections.", default=False)
@click.pass_obj
def collections(obj, timeout, showLoaded):
    """List all collections."""
    try:
        obj.checkConnection()
        click.echo(obj.listCollections(timeout, showLoaded))
    except Exception as e:
        click.echo(message=e, err=True)


@listDetails.command()
@click.option('-c', '--collection', 'collection', help='The name of collection.', default='')
@click.pass_obj
def partitions(obj, collection):
    """List all partitions of the specified collection."""
    try:
        obj.checkConnection()
        validateParamsByCustomFunc(
            obj.getTargetCollection, 'Collection Name Error!', collection)
        click.echo(obj.listPartitions(collection))
    except Exception as e:
        click.echo(message=e, err=True)


@listDetails.command()
@click.option('-c', '--collection', 'collection', help='The name of collection.', default='')
@click.pass_obj
def indexes(obj, collection):
    """List all indexes of the specified collection."""
    try:
        obj.checkConnection()
        validateParamsByCustomFunc(
            obj.getTargetCollection, 'Collection Name Error!', collection)
        click.echo(obj.listIndexes(collection))
    except Exception as e:
        click.echo(message=e, err=True)


@cli.group('describe', no_args_is_help=False)
@click.pass_obj
def describeDetails(obj):
    """Describe collection or partition."""
    pass


@describeDetails.command('collection')
@click.option('-c', '--collection', 'collection', help='The name of collection.', default='')
@click.pass_obj
def describeCollection(obj, collection):
    """
    Describe collection.

    Example:

        milvus_cli > describe collection -c test_collection_insert
    """
    try:
        obj.checkConnection()
        click.echo(obj.getCollectionDetails(collection))
    except Exception as e:
        click.echo(message=e, err=True)


@describeDetails.command('partition')
@click.option('-c', '--collection', 'collectionName', help='The name of collection.', default='')
@click.option('-p', '--partition', 'partition', help='The name of partition.', default=None)
@click.pass_obj
def describePartition(obj, collectionName, partition):
    """
    Describe partition.

    Example:

        milvus_cli > describe partition -c test_collection_insert -p _default
    """
    try:
        obj.checkConnection()
        collection = obj.getTargetCollection(collectionName)
    except Exception as e:
        click.echo(f"Error when getting collection by name!\n{str(e)}")
    else:
        click.echo(obj.getPartitionDetails(collection, partition))


@cli.group('create', no_args_is_help=False)
@click.pass_obj
def createDetails(obj):
    """Create collection, partition and index."""
    pass


@createDetails.command('collection')
@click.option('-c', '--collection-name', 'collectionName', help='Collection name to be created.', default='')
@click.option('-p', '--schema-primary-field', 'primaryField', help='Primary field name.', default='')
@click.option('-a', '--schema-auto-id', 'autoId', help='Enable auto id.', default=False, is_flag=True)
@click.option('-d', '--schema-description', 'description', help='Description details.', default='')
@click.option('-f', '--schema-field', 'fields', help='FieldSchema. Usage is "<Name>:<DataType>:<Dim(if vector) or Description>"', default=None, multiple=True)
@click.pass_obj
def createCollection(obj, collectionName, primaryField, autoId, description, fields):
    """
    Create partition.

    Example:

      create collection -c car -f id:INT64:primary_field -f vector:FLOAT_VECTOR:128 -f color:INT64:color -f brand:INT64:brand -p id -a -d 'car_collection'
    """
    try:
        obj.checkConnection()
        validateCollectionParameter(
            collectionName, primaryField, fields)
    except ParameterException as pe:
        click.echo("Error!\n{}".format(str(pe)))
    except ConnectException as ce:
        click.echo("Error!\n{}".format(str(ce)))
    else:
        click.echo(obj.createCollection(collectionName,
                   primaryField, autoId, description, fields))
        click.echo("Create collection successfully!")


@createDetails.command('partition')
@click.option('-c', '--collection', 'collectionName', help='Collection name.', default='')
@click.option('-p', '--partition', 'partition', help='The name of partition.', default=None)
@click.option('-d', '--description', 'description', help='Partition description.', default='')
@click.pass_obj
def createPartition(obj, collectionName, partition, description):
    """
    Create partition.

    Example:

        milvus_cli > create partition -c car -p new_partition -d test_add_partition
    """
    try:
        obj.checkConnection()
        obj.getTargetCollection(collectionName)
    except Exception as e:
        click.echo(f"Error occurred when get collection by name!\n{str(e)}")
    else:
        click.echo(obj.createPartition(collectionName, description, partition))
        click.echo("Create partition successfully!")


@createDetails.command('index')
@click.pass_obj
def createIndex(obj):
    """
    Create index.

    Example:

        milvus_cli > create index

        Collection name (car, car2): car2

        The name of the field to create an index for (vector): vector

        Index type (FLAT, IVF_FLAT, IVF_SQ8, IVF_PQ, RNSG, HNSW, ANNOY): IVF_FLAT

        Index metric type (L2, IP, HAMMING, TANIMOTO): L2

        Index params nlist: 2

        Timeout []: 
    """
    try:
        obj.checkConnection()
        collectionName = click.prompt(
            'Collection name', type=click.Choice(obj._list_collection_names()))
        fieldName = click.prompt(
            'The name of the field to create an index for', type=click.Choice(obj._list_field_names(collectionName, showVectorOnly=True)))
        indexType = click.prompt(
            'Index type', type=click.Choice(IndexTypes))
        metricType = click.prompt(
            'Index metric type', type=click.Choice(MetricTypes))
        index_building_parameters = IndexTypesMap[indexType]['index_building_parameters']
        params = []
        for param in index_building_parameters:
            tmpParam = click.prompt(
                f'Index params {param}')
            params.append(f'{param}:{tmpParam}')
        inputTimeout = click.prompt('Timeout', default='')
        timeout = inputTimeout if inputTimeout else None
        validateIndexParameter(
            indexType, metricType, params)
    except ParameterException as pe:
        click.echo("Error!\n{}".format(str(pe)))
    except ConnectException as ce:
        click.echo("Error!\n{}".format(str(ce)))
    else:
        click.echo(obj.createIndex(collectionName, fieldName,
                   indexType, metricType, params, timeout))
        click.echo("Create index successfully!")


@cli.group('delete', no_args_is_help=False)
@click.pass_obj
def deleteObject(obj):
    """Delete specified collection, partition and index."""
    pass


@deleteObject.command('collection')
@click.option('-c', '--collection', 'collectionName', help='The name of collection to be deleted.', default='')
@click.option('-t', '--timeout', 'timeout', help='An optional duration of time in seconds to allow for the RPC. If timeout is set to None, the client keeps waiting until the server responds or an error occurs.', default=None, type=int)
@click.pass_obj
def deleteCollection(obj, collectionName, timeout):
    """
    Drops the collection together with its index files.

    Example:

        milvus_cli > delete collection -c car
    """
    click.echo(
        "Warning!\nYou are trying to delete the collection with data. This action cannot be undone!\n")
    if not click.confirm('Do you want to continue?'):
        return
    try:
        obj.checkConnection()
        obj.getTargetCollection(collectionName)
    except Exception as e:
        click.echo(f"Error occurred when get collection by name!\n{str(e)}")
    else:
        result = obj.dropCollection(collectionName, timeout)
        click.echo("Drop collection successfully!") if not result else click.echo(
            "Drop collection failed!")


@deleteObject.command('partition')
@click.option('-c', '--collection', 'collectionName', help='Collection name', default=None)
@click.option('-p', '--partition', 'partition', help='The name of partition.', default=None)
@click.option('-t', '--timeout', 'timeout', help='An optional duration of time in seconds to allow for the RPC. If timeout is set to None, the client keeps waiting until the server responds or an error occurs.', default=None, type=int)
@click.pass_obj
def deletePartition(obj, collectionName, partition, timeout):
    """
    Drop the partition and its corresponding index files.

    Example:

        milvus_cli > delete partition -c car -p new_partition
    """
    click.echo(
        "Warning!\nYou are trying to delete the partition with data. This action cannot be undone!\n")
    if not click.confirm('Do you want to continue?'):
        return
    try:
        obj.checkConnection()
        obj.getTargetCollection(collectionName)
    except Exception as e:
        click.echo(f"Error occurred when get collection by name!\n{str(e)}")
    else:
        result = obj.dropPartition(collectionName, partition, timeout)
        click.echo("Drop partition successfully!") if not result else click.echo(
            "Drop partition failed!")


@deleteObject.command('index')
@click.option('-c', '--collection', 'collectionName', help='Collection name', default=None)
@click.option('-t', '--timeout', 'timeout', help='An optional duration of time in seconds to allow for the RPC. If timeout is set to None, the client keeps waiting until the server responds or an error occurs.', default=None, type=int)
@click.pass_obj
def deleteIndex(obj, collectionName, timeout):
    """
    Drop index and its corresponding index files.

    Example:

        milvus_cli > delete index -c car
    """
    click.echo(
        "Warning!\nYou are trying to delete the index of collection. This action cannot be undone!\n")
    if not click.confirm('Do you want to continue?'):
        return
    try:
        obj.checkConnection()
        obj.getTargetCollection(collectionName)
    except Exception as e:
        click.echo(f"Error occurred when get collection by name!\n{str(e)}")
    else:
        result = obj.dropIndex(collectionName, timeout)
        click.echo("Drop index successfully!") if not result else click.echo(
            "Drop index failed!")


@cli.command()
@click.pass_obj
def search(obj):
    """
    Conducts a vector similarity search with an optional boolean expression as filter.

    Example-1(import a csv file):

        Collection name (car, test_collection): car

        The vectors of search data(the length of data is number of query (nq), 
        the dim of every vector in data must be equal to vector field’s of 
        collection. You can also import a csv file with out headers): examples/import_csv/search_vectors.csv

        The vector field used to search of collection (vector): vector

        Metric type: L2

        Search parameter nprobe's value: 10

        The max number of returned record, also known as topk: 2

        The boolean expression used to filter attribute []: id > 0

        The names of partitions to search(split by "," if multiple) ['_default'] []: _default

    Example-2(collection has index):

        Collection name (car, test_collection): car

        \b
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

        The names of partitions to search(split by "," if multiple) ['_default'] []: _default

        timeout []: 

    Example-3(collection has no index):

        Collection name (car, car2): car

        The vectors of search data(the length of data is number of query (nq), 
        the dim of every vector in data must be equal to vector field’s of 
        collection. You can also import a csv file with out headers): examples/import_csv/search_vectors.csv

        The vector field used to search of collection (vector): vector

        The specified number of decimal places of returned distance [-1]: 5

        The max number of returned record, also known as topk: 2

        The boolean expression used to filter attribute []: 

        The names of partitions to search(split by "," if multiple) ['_default'] []: 

        Timeout []: 
    """
    collectionName = click.prompt(
        'Collection name', type=click.Choice(obj._list_collection_names()))
    data = click.prompt(
        'The vectors of search data(the length of data is number of query (nq), the dim of every vector in data must be equal to vector field’s of collection. You can also import a csv file with out headers)')
    annsField = click.prompt(
        'The vector field used to search of collection', type=click.Choice(obj._list_field_names(collectionName, showVectorOnly=True)))
    indexDetails = obj._list_index(collectionName)
    hasIndex = not not indexDetails
    if indexDetails:
        index_type = indexDetails['index_type']
        search_parameters = IndexTypesMap[index_type]['search_parameters']
        metric_type = indexDetails['metric_type']
        click.echo(f"Metric type: {metric_type}")
        metricType = metric_type
        params = []
        for parameter in search_parameters:
            paramInput = click.prompt(f'Search parameter {parameter}\'s value')
            params += [f"{parameter}:{paramInput}"]
    else:
        metricType = ''
        params = []
    roundDecimal = click.prompt(
        'The specified number of decimal places of returned distance', default=-1, type=int)
    limit = click.prompt(
        'The max number of returned record, also known as topk', default=None, type=int)
    expr = click.prompt(
        'The boolean expression used to filter attribute', default='')
    partitionNames = click.prompt(
        f'The names of partitions to search(split by "," if multiple) {obj._list_partition_names(collectionName)}', default='')
    timeout = click.prompt('Timeout', default='')
    export, exportPath = False, ''
    # if click.confirm('Would you like to export results as a csv File?'):
    #     export = True
    #     exportPath = click.prompt('Directory path to csv file')
    # export = click.prompt('Would you like to export results as a csv File?', default='n', type=click.Choice(['Y', 'n']))
    # if export:
    #     exportPath = click.prompt('Directory path to csv file')
    try:
        searchParameters = validateSearchParams(
            data, annsField, metricType, params, limit, expr, partitionNames, timeout, roundDecimal, hasIndex=hasIndex)
        obj.checkConnection()
    except ParameterException as pe:
        click.echo("Error!\n{}".format(str(pe)))
    except ConnectException as ce:
        click.echo("Error!\n{}".format(str(ce)))
    else:
        if export:
            results = obj.search(
                collectionName, searchParameters, prettierFormat=False)
        else:
            results = obj.search(collectionName, searchParameters)
            click.echo(f"Search results:\n")
            for idx, item in enumerate(results):
                click.echo(f"No.{idx+1}:\n{item}\n")
            # click.echo(obj.search(collectionName, searchParameters))


@cli.command()
@click.pass_obj
def query(obj):
    """
    Query with a set of criteria, and results in a list of records that match the query exactly.

    Example:

        milvus_cli > query

        Collection name: car

        The query expression(field_name in [x,y]): id in [ 427284660842954108, 427284660842954199 ]

        Name of partitions that contain entities(split by "," if multiple) []: default

        A list of fields to return(split by "," if multiple) []: color, brand

        timeout []: 
    """
    collectionName = click.prompt(
        'Collection name', type=click.Choice(obj._list_collection_names()))
    expr = click.prompt('The query expression(field_name in [x,y])')
    partitionNames = click.prompt(
        f'The names of partitions to search(split by "," if multiple) {obj._list_partition_names(collectionName)}', default='')
    outputFields = click.prompt(
        f'Fields to return(split by "," if multiple) {obj._list_field_names(collectionName)}', default='')
    timeout = click.prompt('timeout', default='')
    try:
        queryParameters = validateQueryParams(
            expr, partitionNames, outputFields, timeout)
        obj.checkConnection()
    except ParameterException as pe:
        click.echo("Error!\n{}".format(str(pe)))
    except ConnectException as ce:
        click.echo("Error!\n{}".format(str(ce)))
    else:
        click.echo(obj.query(collectionName, queryParameters))


@cli.command('import')
@click.option('-c', '--collection', 'collectionName', help='The name of collection to be imported.', default=None)
@click.option('-p', '--partition', 'partitionName', help='The partition name which the data will be inserted to, if partition name is not passed, then the data will be inserted to “_default” partition.', default=None)
@click.option('-t', '--timeout', 'timeout', help='An optional duration of time in seconds to allow for the RPC. If timeout is set to None, the client keeps waiting until the server responds or an error occurs.', default=None, type=float)
@click.argument('path')
@click.pass_obj
def importData(obj, collectionName, partitionName, timeout, path):
    """
    Import data from csv file with headers and insert into target collection.

    Example:

        milvus_cli > import 'examples/import_csv/vectors.csv' -c car

        Reading csv file...  [####################################]  100%

        Column names are ['vector', 'color', 'brand']

        Processed 50001 lines.

        Import successfully.
    """
    try:
        obj.checkConnection()
        validateParamsByCustomFunc(
            obj.getTargetCollection, 'Collection Name Error!', collectionName)
        result = readCsvFile(path.replace('"', '').replace("'", ""))
        data = result['data']
        click.secho('Inserting ...', blink=True, bold=True)
        entitiesNum = obj.insert(collectionName, data, partitionName, timeout)
    except Exception as e:
        click.echo("Error!\n{}".format(str(e)))
    else:
        click.echo(f"Insert successfully.\nTotal entities: {entitiesNum}")


@cli.command('exit')
def quitapp():
    """Exit the CLI."""
    global quitapp
    quitapp = True


quitapp = False  # global flag
comp = Completer()


def runCliPrompt():
    args = sys.argv
    if args and (args[-1] == '--version'):
        print(f"Milvus Cli v{getPackageVersion()}")
        return
    try:
        while not quitapp:
            import readline
            readline.set_completer_delims(' \t\n;')
            readline.parse_and_bind("tab: complete")
            readline.set_completer(comp.complete)
            astr = input('milvus_cli > ')
            try:
                cli(astr.split())
            except SystemExit:
                # trap argparse error message
                # print('error', SystemExit)
                continue
            except ParameterException as pe:
                click.echo(message=f"{str(pe)}", err=True)
            except ConnectException as ce:
                click.echo(
                    message="Connect to milvus Error!\nPlease check your connection.", err=True)
            except Exception as e:
                click.echo(
                    message=f"Error occurred!\n{str(e)}", err=True)
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)


if __name__ == '__main__':
    runCliPrompt()
