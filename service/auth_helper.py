import requests
import json
import datetime
import urllib.parse
import adal
from flask import jsonify 
import logging

"""
Base URL where to send token request
Placeholder contains Azure tenant id
"""
TOKEN_URL = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"
RESOURCE = "https://graph.microsoft.com"

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
    

def add_token_to_cache(client_id: str, tenant_id: str, token_obj: dict) -> None:
    """
    Function to add an access token for given client and tenant into token cache
    :param client_id:i d you get after register new app in Azure AD
    :param tenant_id: enant id may be found in Azure Admin Center -> Overview -> Properties
    :param token_obj: Oauth2 token object
    :return: None
    """
    logging.info("add_token_to_cache")
    __token_cache[client_id + tenant_id] = token_obj


def get_token(client_id, client_secret, tenant_id, refresh_token):
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
        r_token = refresh_token.replace('refresh_token', 'refreshToken')
        __token_cache[client_id + tenant_id] = get_new_token_with_refresh_token(r_token, client_id, tenant_id)
    logging.info("get_token")
    return __token_cache.get(client_id + tenant_id)


def get_tokens_as_app(client, user_code_info, tenant):
    """
    Function to use adal lib to get tokens as an app
    :param resource: https://graph.microsoft.com
    :param client: id you get after register new app in Azure AD
    """
    authority = "https://login.microsoftonline.com/" + tenant

    context = adal.AuthenticationContext(authority)
    r_token = None
    
    if r_token is None:
        res = context.acquire_token_with_device_code(RESOURCE, user_code_info, client)
        r_token =res.get('refreshToken')
    
    token_obj = context.acquire_token_with_refresh_token(r_token, client, RESOURCE, client_secret=None)

    # Formatting
    token_obj['timestamp'] = datetime.datetime.now().timestamp()
    token_obj['refresh_token'] = token_obj.pop('refreshToken')
    token_obj['access_token'] = token_obj.pop('accessToken')
    token_obj['token_type'] = token_obj.pop('tokenType')
    token_obj['expires_in'] = token_obj.pop('expiresIn')
    token_obj['scope'] = 'https://graph.microsoft.com/.default, offline_access, Group.Read.All'
    token_obj['grant_type'] = 'authorization_code'
    token_obj['expires_in'] = 3600
    token_obj.pop('expiresOn')
    logging.info("get_token_as_app")
    return token_obj


def sign_in_redirect_as_app(client_id, tenant):

    authority = "https://login.microsoftonline.com/" + tenant

    context = adal.AuthenticationContext(authority)
    # Use this for Resource Owner Password Credentials (ROPC)  
    user_code_info = context.acquire_user_code(RESOURCE, client_id)
    logging.info("sign_in_redirect_as_app")
    return user_code_info


def get_new_token_with_refresh_token(r_token, client_id, tenant_id):

    authority = "https://login.microsoftonline.com/" + tenant_id

    context = adal.AuthenticationContext(authority)

    token_obj = context.acquire_token_with_refresh_token(r_token, client_id, RESOURCE, client_secret=None)

    # Formatting
    token_obj['timestamp'] = datetime.datetime.now().timestamp()
    token_obj['refresh_token'] = token_obj.pop('refreshToken')
    token_obj['access_token'] = token_obj.pop('accessToken')
    token_obj['token_type'] = token_obj.pop('tokenType')
    token_obj['expires_in'] = token_obj.pop('expiresIn')
    token_obj['scope'] = 'https://graph.microsoft.com/.default, offline_access, Group.Read.All'
    token_obj['grant_type'] = 'authorization_code'
    token_obj['expires_in'] = 3600
    token_obj.pop('expiresOn')
    logging.info("get_new_token_with_refresh_token")

    return token_obj


