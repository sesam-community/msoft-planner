import logging
from dao_helper import get_all_objects, make_request, GRAPH_URL, is_object_already_exists_exception, \
    clear_sesam_attributes, stream_as_json, get_object

from createplannerobjects import CreatePlannerBuckets

RESOURCE_PATH = '/planner/buckets/'

def get_all_buckets(delta=None):
    """
    Fetch and stream back groups from Azure AD via MS Graph API
    :param delta: delta token from last request
    :return: generated JSON output with all fetched groups
    """
    yield from stream_as_json(get_all_objects(f'{RESOURCE_PATH}delta', delta))

def get_buckets(plan_id):
    return get_object(f'/planner/buckets/{plan_id}/')

def create_buckets(bucket_data_list):
    """
    Function to create a bucket
    :param bucke_data_list: json object with group details, must contain plan identifier
    :param task_data: {title:string, percentComplete:int, dueDate:dateTimeTimeZone, assigneePriority: string, bucketId:string}
    :return: string
    Arbitrairy max number of tasks with same name set at 20. change range if needed
    """
    CB = CreatePlannerBuckets()
    return CB.create_object(bucket_data_list)
