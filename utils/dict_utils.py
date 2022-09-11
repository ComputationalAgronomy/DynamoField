
def merge_dicts(partition_key, sort_key, attributes_data):
    try:
        json_data = partition_key | sort_key | attributes_data   # python 3.9 only
    except TypeError:
        json_data = {**partition_key, **sort_key, **attributes_data}
    return json_data
