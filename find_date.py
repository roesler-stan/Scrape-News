import datetime

def find_date(folder, input_directory):
    """ Put this in general parsing file """
    date_str = folder.split(input_directory + '/')[-1]
    items = date_str.split('_')
    items = [int(item) for item in items]
    year = items[0]
    month = items[1]
    day = items[2]
    hour = items[3]
    minute = items[4]
    date = datetime.datetime(year, month, day, hour, minute)
    return date