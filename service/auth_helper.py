import requests
import json
import datetime
import urllib.parse

"""
Base URL where to send token request
Placeholder contains Azure tenant id
"""
TOKEN_URL = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"

"""
We use client_credentials flow with client_id and secret_id

Scope https://graph.microsoft.com/.default means app will have all permissions assigned to it 
in Azure Active Directory ( https://aad.portal.azure.com -> Dashboard -> App Registrations)
"""
TOKEN_REQUEST_PAYLOAD = data = {'grant_type': 'client_credentials',
                                'scope': 'https://graph.microsoft.com/.default'}

"""
Token cache
"""
__token_cache = {}


def check_if_tokens_exist_in_env(environ_generated_token, env_access_token, env_refresh_token):
    environ_generated_token = {
        'token_type': 'Bearer', 
        'scope': 'profile openid email https://graph.microsoft.com/Directory.ReadWrite.All https://graph.microsoft.com/Group.Read.All https://graph.microsoft.com/Group.ReadWrite.All https://graph.microsoft.com/Tasks.Read https://graph.microsoft.com/Tasks.Read.Shared https://graph.microsoft.com/User.Read https://graph.microsoft.com/.default', 
        'expires_in': 36000, 
        'ext_expires_in': 36000,
        'access_token' : env_access_token,
        'refresh_token': env_refresh_token,
        'timestamp' : datetime.datetime.now().timestamp()
    }    

    return environ_generated_token
    
    

def add_token_to_cache(client_id: str, tenant_id: str, token_obj: dict) -> None:
    """
    Function to add an access token for given client and tenant into token cache
    :param client_id:i d you get after register new app in Azure AD
    :param tenant_id: enant id may be found in Azure Admin Center -> Overview -> Properties
    :param token_obj: Oauth2 token object
    :return: None
    """
    __token_cache[client_id + tenant_id] = token_obj


def _get_token(client_id, client_secret, tenant_id):
    """
    Function for getting Oauth2 token by using clint_credentials grant type

    :param client_id: id you get after register new app in Azure AD
    :param client_secret: secret you get after register new app in Azure AD
    :param tenant_id: tenant id may be found in Azure Admin Center -> Overview -> Properties
    :return: oauth token object with timestamp added
    """
    token_url = TOKEN_URL.format(tenant_id)
    response = requests.post(token_url, data=data, verify=True, allow_redirects=False,
                             auth=(client_id, client_secret))
    response.raise_for_status()
    token_obj = json.loads(response.text)
    if not token_obj.get('access_token'):
        raise Exception("access_token not found in response")

    token_obj['timestamp'] = datetime.datetime.now().timestamp()

    return token_obj


def _refresh_token(client_id, client_secret, tenant_id, r_token):
    """
    Function to refresh an Ouath2 token with refresh token
    :param client_id: id you get after register new app in Azure AD
    :param client_secret:  secret you get after register new app in Azure AD
    :param tenant_id: tenant id may be found in Azure Admin Center -> Overview -> Properties
    :param r_token: previously obtained refresh token
    :return: Oauth2 token object
    """
    token_url = TOKEN_URL.format(tenant_id)
    _data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default, offline_access',
        'grant_type': 'refresh_token',
        'refresh_token': r_token
    }
    response = requests.post(token_url, data=_data, verify=True, allow_redirects=False)
    response.raise_for_status()
    if not token_obj.get('access_token'):
        raise Exception("access_token not found in response")

    token_obj['timestamp'] = datetime.datetime.now().timestamp()

    return token_obj


def get_token(client_id, client_secret, tenant_id):
    """
    Function to obtain Oauth token. This function search valid token in cache first and request it
    only when not found or if expired

    :param client_id: id you get after register new app in Azure AD
    :param client_secret: secret you get after register new app in Azure AD
    :param tenant_id: tenant id may be found in Azure Admin Center -> Overview -> Properties
    :return: oauth token object with timestamp added
    """
    token = __token_cache.get(client_id + tenant_id)
    ts = datetime.datetime.now().timestamp()

    if not token or token['timestamp'] + token['expires_in'] + 5 < ts:
        if token and 'refresh_token' in token:
            r_token = token['refresh_token']
            __token_cache[client_id + tenant_id] = _refresh_token(client_id, client_secret, tenant_id, r_token)
        else:
            __token_cache[client_id + tenant_id] = _get_token(client_id, client_secret, tenant_id)

    return __token_cache.get(client_id + tenant_id)


def get_token_on_behalf_of_user(tenant_id, client_id, client_secret, username, password):
    """
    Function to obtain an access_token on behalf on user without signing user in personally (browserless)
    It uses "resource owner password" auth schema
    https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth-ropc
    Only users without 2factor auth could be used for authentication
    :param client_id: id you get after register new app in Azure AD
    :param client_secret: secret you get after register new app in Azure AD
    :param tenant_id: tenant id may be found in Azure Admin Center -> Overview -> Properties
    :param username: username for an registered user
    :param password: users password
    :return: Oauth token object with timestamp of issue
    """
    token_url = TOKEN_URL.format(tenant_id)
    _data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
        'tenant': tenant_id,
        'grant_type': 'password',
        'username': username,
        'password': password
    }
    response = requests.post(token_url, data=_data, verify=True, allow_redirects=False)
    response.raise_for_status()
    token_obj = json.loads(response.text)
    if not token_obj.get('access_token'):
        raise Exception("access_token not found in response")

    token_obj['timestamp'] = datetime.datetime.now().timestamp()

    return token_obj


def get_token_with_auth_code(tenant_id, client_id, client_secret, code, redirect_url):
    """

    :param client_id: id you get after register new app in Azure AD
    :param client_secret: secret you get after register new app in Azure AD
    :param tenant_id: tenant id may be found in Azure Admin Center -> Overview -> Properties
    :param code:  authorization code obtained in Authorization request
    :param redirect_url: where to redirect response with token (must be registered in app properties in Azure)
    :return: token object
    """
    token_url = TOKEN_URL.format(tenant_id)
    _data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default, offline_access',
        'code': code,
        'redirect_uri': redirect_url,
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_url, data=_data, verify=True, allow_redirects=False)
    response.raise_for_status()
    token_obj = json.loads(response.text)
    if not token_obj.get('access_token'):
        raise Exception("access_token not found in response")

    token_obj['timestamp'] = datetime.datetime.now().timestamp()

    return token_obj

def get_authorize_url(tenant, client, state, r_url):
    """
    Function to built URL for authorization request
    :param tenant: tenant id may be found in Azure Admin Center -> Overview -> Properties
    :param client: id you get after register new app in Azure AD
    :param state: randomly generated unique value used for preventing cross-site request forgery attacks
    :param r_url: where to redirect response with auth code (must be registered in app properties in Azure)
    :return: built URL
    """
    scope = urllib.parse.quote('https://graph.microsoft.com/.default')
    base_url = 'https://login.microsoftonline.com'
    path = 'oauth2/v2.0/authorize'
    r_url = f'redirect_uri={urllib.parse.quote(r_url)}'
    r_type = 'response_type=code'
    r_mode = 'response_mode=query'
    
    return f'{base_url}/{tenant}/{path}?client_id={client}&{r_type}&{r_url}&{r_mode}&scope={scope}&state={state}'
