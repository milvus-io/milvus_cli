from Types import ParameterException
import os


def readCsvFile(path='', withCol=True):
    if not path or not path[-4:] == '.csv':
        raise ParameterException('Path is empty or target file is not .csv')
    fileSize = os.stat(path).st_size
    if fileSize >= 512000000:
        raise ParameterException(
            'File is too large! Only allow csv files less than 512MB.')
    from csv import reader
    from json import JSONDecodeError
    import click
    try:
        result = {'columns': [], 'data': []}
        with click.open_file(path, 'r') as csv_file:
            click.echo(f'Opening csv file({fileSize} bytes)...')
            csv_reader = reader(csv_file, delimiter=',')
            # For progressbar, transform it to list.
            rows = list(csv_reader)
            line_count = 0
            with click.progressbar(rows, label='Reading csv rows...', show_percent=True) as bar:
                # for row in csv_reader:
                for row in bar:
                    if withCol and line_count == 0:
                        result['columns'] = row
                        line_count += 1
                    else:
                        formatRowForData(row, result['data'])
                        line_count += 1
            click.echo(f'''Column names are {result['columns']}''')
            click.echo(f'Processed {line_count} lines.')
    except FileNotFoundError as fe:
        raise ParameterException(f'FileNotFoundError {str(fe)}')
    except UnicodeDecodeError as ue:
        raise ParameterException(f'UnicodeDecodeError {str(ue)}')
    except JSONDecodeError as je:
        raise ParameterException(f'JSONDecodeError {str(je)}')
    else:
        return result


# For readCsvFile formatting data.
def formatRowForData(row=[], data=[]):
    from json import loads
    # init data with empty list
    if not data:
        for _in in range(len(row)):
            data.append([])
    for idx, val in enumerate(row):
        formattedVal = loads(val)
        data[idx].append(formattedVal)


def writeCsvFile(path, rows, headers=[]):
    if not path:
        raise ParameterException(f'Path should not be empty')
    from csv import writer
    import click
    try:
        with click.open_file(path, 'w+') as csv_file:
            csv_writer = writer(csv_file, delimiter=',')
            if headers:
                csv_writer.writerow(headers)
            line_count = 0
            with click.progressbar(rows, label='Writing csv rows...', show_percent=True) as bar:
                for row in bar:
                    csv_writer.writerow(row)
                    line_count += 1
            click.echo(f'Processed {line_count} lines.')
    except Exception as e:
        raise ParameterException(f'Export csv file error! {str(e)}')
