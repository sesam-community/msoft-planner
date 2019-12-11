import logging
import requests
import json
import os
from auth_helper import get_token
from urllib.parse import urlparse, parse_qs

# Available values: v1.0, beta
GRAPH_URL = f'https://graph.microsoft.com/{os.environ.get("API_VERSION", "v1.0")}'

ALLOWED_METHODS = ['get', 'post', 'put', 'patch']

METADATA = os.environ.get('ODATA_METADATA', 'minimal')

__token = None

def init_dao(client_id: str, client_secret: str, tenant_id: str, refresh_token) -> None:
    global __token
    __token = get_token(client_id, client_secret, tenant_id, refresh_token)

def make_request(url: str, method: str,  data=None) -> dict:
    """
    Function to send request to given URL with given method using given token
    :param url: where to send request
    :param method: which method to use. An exception will be thrown if method is not allowed
    :param data: request payload for POST/PUT/PATCH requests
    :return: decoded JSON object
    """
    if method.lower() not in ALLOWED_METHODS:
        raise Exception(f'Method {method} is not allowed')

    if not __token:
        raise ValueError("access token not found, you need to authenticate before")

    t_type = __token['token_type']
    t_value = __token['access_token']
    headers = {
        'Authorization': f'{t_type} {t_value}',
        "Accept": f'application/json;odata.metadata={METADATA};odata.streaming=true'
    }

    """
    for update using PATCH method, added If_Match statement in header with check for last known ETag value 
    """
    if method != 'GET':
        headers['Content-Type'] = 'application/json'
        if method == 'PATCH':
            try:
                etag= data.get('@odata.etag')
                print(etag)
                headers['If_Match']= f'{etag}'
                print("Headers:\t", headers)
            except error as e:
                print("PATCH error ", e)



    call_method = getattr(requests, method.lower())
    api_call_response = call_method(url, headers=headers, verify=True, json=data)
    #if not api_call_response.ok:
    #    pass
    #else:
    #    api_call_response.raise_for_status()
    try:
        api_call_response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        logging.error(error)
        logging.error(error.response.text)
        raise error

    return json.loads(api_call_response.text) if len(api_call_response.text) > 0 else {}


def get_all_objects(resource_path: str, delta=None):
    """
    Fetch and stream back objects from MS Graph API
    :param resource_path path to needed resource in MS Graph API
    :param delta: delta token from last request.
    More about delta https://docs.microsoft.com/en-us/graph/delta-query-users
    :return: generated output with all fetched objects
    """
    url = GRAPH_URL + resource_path

    if delta:
        url += f'?$deltatoken={delta}'

    while url is not None:
        result = make_request(url, 'get')

        logging.debug(f"Got response: {json.dumps(result, indent=4, sort_keys=True)}")

        if result.get('@odata.deltaLink'):
            parsed_url = urlparse(result.get('@odata.deltaLink'))
            query = parse_qs(parsed_url.query)
            delta = query['$deltatoken'][0]

        if type(result.get('value')) == list:
            for item in result['value']:
                item['_updated'] = delta
                item['_id'] = item['id']
                yield item
        else:
            raise ValueError(f'value object expected in response to url: {url} got {result}')

        url = result.get('@odata.nextLink', None)


def get_object(resource_path):
    url = GRAPH_URL + resource_path
    result = make_request(url, 'get')

    logging.debug(f"Got response: {json.dumps(result, indent=4, sort_keys=True)}")

    return result


def stream_as_json(generator_function):
    """
    Stream list of objects as JSON array
    :param generator_function:
    :return:
    """
    first = True

    yield '['

    for item in generator_function:
        if not first:
            yield ','
        else:
            first = False

        yield json.dumps(item)

    yield ']'


def is_object_already_exists_exception(ex: requests.exceptions.HTTPError) -> bool:
    """
    Check exception details to find if this is a 'Already exists' exceptions or not
    :param ex: HTTPError object
    :return: True if exception is about already existing object or false otherwise
    """
    exc_details = json.loads(ex.response.text)
    if exc_details.get('error').get('details') and exc_details['error']['details'][0]['code'] == 'ObjectConflict':
        return True
    return False


def clear_sesam_attributes(sesam_object: dict):
    """
    Return same dict but without properties starting with "_"
    :param sesam_object: input object from Sesam
    :return: object cleared from Sesam properties
    """
    return {k: v for k, v in sesam_object.items() if not k.startswith('_')}
