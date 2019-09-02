from flask import Flask, request, jsonify, Response, session, redirect
import json
import datetime
from datetime import timedelta
import webbrowser
import logging
import requests
import uuid
import os
from logger_helper import log_request
from auth_helper import get_authorize_url, get_token_with_auth_code, add_token_to_cache, check_if_tokens_exist_in_env, get_r_token_as_app, get_a_token_as_app ,sign_in_redirect_as_app
from dao_helper import init_dao, get_all_objects, init_dao_on_behalf_on, stream_as_json
from plans_nd_tasks import get_plans, get_tasks
from planner_groups import get_all_groups
from planner_users import get_all_users
from planner_buckets import get_all_buckets, get_buckets

app = Flask(__name__)

os.environ['client_id'] = 'b0895e31-7492-43b6-8837-d223f2cd4c07'
os.environ['client_secret'] = 'HUdR*0e+QICoKvjbSQNCv8GdKQ4wU6/_'
os.environ['tenant_id'] = '7bcbcc45-fb12-41d3-8ace-fa0fffaebf1d'
os.environ['redirect_url'] = 'http://localhost:5000/auth'
#os.environ['access_token'] = 'eyJ0eXAiOiJKV1QiLCJub25jZSI6IlpBUC15TFh2UlQ5QXpfa2xiOGc3M3VYWjVhOWFrWGx3RDhab2x6ajhwVTQiLCJhbGciOiJSUzI1NiIsIng1dCI6ImllX3FXQ1hoWHh0MXpJRXN1NGM3YWNRVkduNCIsImtpZCI6ImllX3FXQ1hoWHh0MXpJRXN1NGM3YWNRVkduNCJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC83YmNiY2M0NS1mYjEyLTQxZDMtOGFjZS1mYTBmZmZhZWJmMWQvIiwiaWF0IjoxNTY1OTQxNzM2LCJuYmYiOjE1NjU5NDE3MzYsImV4cCI6MTU2NTk0NTYzNiwiYWNjdCI6MCwiYWNyIjoiMSIsImFpbyI6IkFVUUF1LzhNQUFBQVhwRUFiVzNTMi9MRDQyd2lTaDFTM29XT1c4Qm4veVNMQlFQOGt2cG1UUmt3bUpLWTFDS2xLalNsNU50NW9ueWdiNkNpY09ESk5PSHU3Z3kwbGRQaTJnPT0iLCJhbXIiOlsicHdkIiwibWZhIl0sImFwcF9kaXNwbGF5bmFtZSI6IlBsYW5uZXJDb25uZWN0b3JOYXRpdmUiLCJhcHBpZCI6ImIwODk1ZTMxLTc0OTItNDNiNi04ODM3LWQyMjNmMmNkNGMwNyIsImFwcGlkYWNyIjoiMCIsImlwYWRkciI6IjE4NS4xMy45Mi4yNCIsIm5hbWUiOiJKb25hcyBBbHMgQ2hyaXN0ZW5zZW4iLCJvaWQiOiJmNzNkN2Q1OS03MzEwLTQxNjEtYTNhZS03ZjIzZTMyYmQwYWYiLCJwbGF0ZiI6IjE0IiwicHVpZCI6IjEwMDMyMDAwNEI0OTMzM0MiLCJzY3AiOiJEaXJlY3RvcnkuUmVhZFdyaXRlLkFsbCBHcm91cC5SZWFkV3JpdGUuQWxsIFRhc2tzLlJlYWQgVGFza3MuUmVhZC5TaGFyZWQgVXNlci5SZWFkIiwic2lnbmluX3N0YXRlIjpbImlua25vd25udHdrIiwia21zaSJdLCJzdWIiOiJKTXV2TFNvemRBUGJlQzhJMzJ5RkMwMkhpZXJTQVdmUjFWeDFWdk9aSmtvIiwidGlkIjoiN2JjYmNjNDUtZmIxMi00MWQzLThhY2UtZmEwZmZmYWViZjFkIiwidW5pcXVlX25hbWUiOiJqb25hcy5jaHJpc3RlbnNlbkBzZXNhbS5pbyIsInVwbiI6ImpvbmFzLmNocmlzdGVuc2VuQHNlc2FtLmlvIiwidXRpIjoidlBDRFJnNDdHVVNNU2J6eDVTUWFBQSIsInZlciI6IjEuMCIsInhtc190Y2R0IjoxNTQzNDAxODE5fQ.VASa8BZ1AWv9DesRFQjgUNM_cJmjw__QGe9NJllK91XPYgwSVMdwRrG7eAIPXn8ZOEj1Q898cUxvbfdJvkpO9PJtzlMXP0VBHPn80B75uST2TztUuzvWLIX8i0OR4it1cl-TGorWECUdmnZ0z8e2VPCJePs9zmbk-NV6MK5wiXePbqjuxnYskOIBrJMb_iDsgZlyvYBQ3fnG1QPC86NVDGTT_EVbB1NyQ58hLqjUQmytxI3k61S1mJ3n4UBbvqe1w16GbR-Gg2oiazS04HKgjmH0ssfD_mkpfBlUZ3bvNikwItRXivxiUfTjRXX9Evl70hJwWLT2rUH08DBDX8UnOw'
#os.environ['refresh_token'] = 'AQABAAAAAAAP0wLlqdLVToOpA4kwzSnx4Ns20jxfXSlPBfDoyAbhm-5VR2Npz4uyBkMjsJL0ryIJjztRsmrxFV2nlVxSGlPFu0xXjjng16kHugfylGU88TVH3Of1T6gl3tJeScyOWGEpRI-lVgbmpAAJJTm8XmIG_CeHbXBCgAt-32yO9o2t1RwfWfu52NMgGiSbba-PJGj0Aa4An1rKUS7J19UYWP0nLhxoaNknvOKvYWRrzwFMYpcR7XVLWNBAARdoQT2tQP6ek9UtNl5cWrbEy5ocSvvS5UXDW5kKuWYyT4fALAYHQobGZJ_d4vhFbbQs2hnc_BYJii4DbKH1A2kCpmLrfDB-r8UL5ySR9EuR0h0XVMZ6touLF1i8LvAra84Ztzj270pkaPc7C9morfYGn3BRdRG1wj8YHDEf74z9hLp63rytTqfBmSMjYgp9rq7tAXNOa9dD_3y-XIfirsgUCuEYCuy0II_iESdgbgJq6YBYewvdJ32nLunCB6zXCSpH5_vh-D4xnV_i-j3qUeIJptdvqILujg2EndSA4iJmSL3PDSeTZoEv3AVBq-pNP4dAxwRyFG3SypKNjMOTbbrJulhk1Sp_iikkwXWV-hITGD9PRbBKZzBzAJ0a5a7ny6vBC4TRF3ONSc4c6NdyrxRgLVafiT733dZESgu5fFaWS65sDA0htcGx5Z4vP9Cp9kK4v0gJD3FF83T61q5JwtEgsyQ302BA1obiB8Rlmz6FSQeYf087vLcv-QF-6fqaQDZydEsPMderuDF6v4tnsTNjsSUC8I1eIg7AaK_eW84Bp_TyiIP1Bq6O0KnpGdqXjZNR2vKFuqiH4lii-RbBlWGnQdTIiyxorGTXIy922SVs33cvTlckiHdd6hkzVRjd6SDFXbFUDgs3R8iVWkBLF0mQLoJ5RIc7_TgzGtRuT40UoXJc2gVn5iAA'

env = os.environ.get

client_id = env('client_id')
client_secret = env('client_secret')
tenant_id = env('tenant_id')
redirect_url = env('redirect_url')
env_access_token = env('access_token')
env_refresh_token = env('refresh_token')

logger = None
token = dict()
user_code_info = None

# used to encrypt user sessions
app.secret_key = uuid.uuid4().bytes

required_env_vars = ['client_id', 'client_secret', 'tenant_id']
missing_env_vars = list() 

## Helper functions
def check_env_variables(required_env_vars, missing_env_vars):
    for env_var in required_env_vars:
        value = os.getenv(env_var)
        if not value:
            missing_env_vars.append(env_var)
        
    if len(missing_env_vars) != 0:
        app.logger.error(f"Missing the following required environment variable(s) {missing_env_vars}")
        sys.exit(1)

@app.route('/')
def index():
    global user_code_info
    if user_code_info is None:
        user_code_info = sign_in_redirect_as_app(client_id, tenant_id)

        output = {
            'service': 'Microsoft Planner Connector',
            'remote_addr': request.remote_addr,
            'To get tokens' : f"{user_code_info.get('message')}",
            'After getting tokens' : 'go to /auth to aquire and save tokens'
        }

        return jsonify(output)

    if env('access_token') is not None:
        output = {
            'service': 'Microsoft Planner Connector',
            'remote_addr': request.remote_addr,
            'To get tokens' : 'Go to /auth to aquire and save tokens'
        }
        
        return jsonify(output)


@app.route('/auth', methods=['POST', 'GET'])
@log_request
def auth_user():
    """
    Endpoint to sign in user interactively by using Microsoft login page
    :return:
    """

    global token
    global user_code_info
    app.logger.info("Microsoft Planner Service running on /auth port as expected")
    #if not request.args.get('code'):
    #    return redirect(get_authorize_url(tenant_id, client_id, redirect_url))
    #code = request.args.get('code')
    if token is None:
        app.logger.info('Requesting access token..')
        r_token = get_r_token_as_app(client_id, user_code_info, tenant_id)
        token = get_a_token_as_app(client_id, r_token)
        #token = get_token_with_auth_code(tenant_id, client_id, client_secret, code, redirect_url)
    if token['expires_in'] <= 10:
        token = get_a_token_as_app(client_id, token['refresh_token'])
        app.logger.info('Access token has been refreshed...')
    if 'access_token' in token:
        app.logger.info('Adding access token to cache...')
        add_token_to_cache(client_id, tenant_id, token)
        return_object = {
            'status': 'Created token for the graph API',
            'to do': 'Use the below provided values to create the tokens in the Datahub tab under Settings in SESAM',
            'name of secret = msgraph-access-token' : f"value of secret = {token['access_token']}",
            'name of secret = msgraph-refresh-token' : f"value of secret = {token['refresh_token']}"
        }
        return Response(json.dumps(return_object), content_type='application/json')
    else:
        app.logger.info("token response malformed")


@app.route('/planner/<var>', methods=['GET', 'POST'])
@log_request
def list_all_tasks(var):
    """
    Endpoint for calling Graph API
    """
    global token
    if token['expires_in'] <= 10:
        token = get_a_token_as_app(client_id, token['refresh_token'])
        app.logger.info('Access token has been refreshed...')
        add_token_to_cache(client_id, tenant_id, token)
    
    init_dao(client_id, client_secret, tenant_id)
    if var.lower() == "tasks":
        app.logger.info(f'Requesting {var} from the graph API')
        return Response(stream_as_json(get_tasks(get_plans(get_all_objects('/groups/')))), content_type='application/json')
    elif var.lower() == "plans":
        app.logger.info(f'Requesting {var} from the graph API')
        return Response(stream_as_json(get_plans(get_all_objects('/groups/'))), request.args.get('since'), content_type='application/json')
    elif var.lower() == "groups":
        app.logger.info(f'Requesting {var} from the graph API')
        return Response(get_all_groups(request.args.get('since')), content_type='application/json')
    elif var.lower() == "users":
        app.logger.info(f'Requesting {var} from the graph API')
        return Response(get_all_users(request.args.get('since')), content_type='application/json')
    else:
        app.logger.warning(f'The following request value : {var} \n - does not comply with what is currently configured backend')
        return Response(json.dumps({"You need to choose a configured <value> in the path '/planner/<value>'" : "I.e. : 'tasks', 'plans', 'groups' or 'users'"}), content_type='application/json')


if __name__ == '__main__':
    # Set up logging
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('microsoftplanner-connector')

    # Log to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)