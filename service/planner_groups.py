import logging
from dao_helper import get_all_objects, make_request, GRAPH_URL, is_object_already_exists_exception, \
    clear_sesam_attributes, stream_as_json

RESOURCE_PATH = '/groups/'


def sync_group_array(group_data_array):
    def __try_create(group_data):
        """
        Internal function to create a group
        :param group_data: json object with group details
        :return: void
        """
        logging.info(f'trying to create group {group_data.get("displayName")}')
        make_request(f'{GRAPH_URL}{RESOURCE_PATH}', 'POST', group_data)
        logging.info(f'group {group_data.get("displayName")} created successfully')

    def __try_update(group_data):
        """
        Internal function to update a group
        :param group_data: json object with group details, must contain group identifier
        :return: void
        """
        group_id = group_data['id'] if 'id' in group_data else None

        if not group_id:
            raise Exception("Couldn't find id for group")

        logging.info(f'trying to update group {group_data.get("displayName")}')
        make_request(f'{GRAPH_URL}{RESOURCE_PATH}{group_id}', 'PATCH', group_data)
        logging.info(f'group {group_data.get("displayName")} updated successfully')

    def __try_delete(group_data):
        """
        Internal function to delete a group
        :param group_data: json object with group details, must contain group identifier
        :return: void
        """
        group_id = group_data['id'] if 'id' in group_data else None
        if not group_id:
            raise Exception("Couldn't find id for group")

        logging.info(f'trying to delete group {group_data.get("displayName")}')
        make_request(f'{GRAPH_URL}{RESOURCE_PATH}{group_id}', 'DELETE')
        logging.info(f'group {group_data.get("displayName")} disabled successfully')

    for group in group_data_array:
        if '_deleted' in group and group['_deleted']:
            __try_delete(group)
            continue

        group = clear_sesam_attributes(group)
        try:
            __try_create(group)
        except Exception as e:
            if is_object_already_exists_exception(e):
                __try_update(group)
            else:
                raise Exception from e


def get_all_groups(delta=None):
    """
    Fetch and stream back groups from Azure AD via MS Graph API
    :param delta: delta token from last request
    :return: generated JSON output with all fetched groups
    """
    yield from stream_as_json(get_all_objects(f'{RESOURCE_PATH}delta', delta))
