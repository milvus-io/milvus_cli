import click
import os
from tabulate import tabulate
from pymilvus_orm import connections


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
def load(obj):
    """Load specified collection."""
    pass



@cli.group()
@click.pass_obj
def list(obj):
    """List collections, partitins and indexes."""
    pass


@list.command()
@click.option('--timeout', 'timeout', help="[Optional] - An optional duration of time in seconds to allow for the RPC. When timeout is set to None, client waits until server response or error occur.", default=None)
@click.option('--using', 'using', help="[Optional] - Milvus link of create collection.", default='default')
@click.option('--show-loaded', 'showLoaded', help="[Optional] - Only show loaded collections.", default=False)
@click.pass_obj
def collections(obj, timeout, using, showLoaded):
    click.echo(obj.listCollections(timeout, using, showLoaded))


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
