import logging
from dao_helper import get_all_objects, make_request, GRAPH_URL, is_object_already_exists_exception, \
    clear_sesam_attributes, stream_as_json, get_object

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

