from flask import Flask, request, jsonify, Response, session, redirect
import json
import datetime
import logging
import uuid
import os
from logger_helper import log_request
from auth_helper import get_authorize_url, get_token_with_auth_code, add_token_to_cache, get_token_on_behalf_of_user
from dao_helper import init_dao, get_all_objects, init_dao_on_behalf_on, stream_as_json
from plan_dao import get_plans, get_tasks

app = Flask(__name__)

env = os.environ.get

client_id = env('client_id')
client_secret = env('client_secret')
tenant_id = env('tenant_id')
username = env('username')
password = env('password')
redirect_url = env('redirect_url')

logger = None

# used to encrypt user sessions
app.secret_key = uuid.uuid4().bytes

required_env_vars = ['client_id', 'client_secret', 'tenant_id', 'username', 'password', 'redirect_url']
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

## Merge helper function
def dict_merger(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res 


@app.route('/')
def index():
    output = {
        'service': 'Microsoft Planner Connector',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)


@app.route('/auth', methods=['GET'])
@log_request
def auth_user():
    """
    Endpoint to sign in user interactively by using Microsoft login page
    :return:
    """
    state = str(datetime.datetime.now().timestamp()) if 'state' not in session else session['state']

    if not request.args.get('code'):
        session['state'] = state
        return redirect(get_authorize_url(tenant_id, client_id, state, redirect_url))
    else:
        code = request.args.get('code')
        returned_state = request.args.get('state')
        if state != returned_state:
            print(state)
            print(returned_state)
            raise SystemError("Response state doesn't match request state")

        token = get_token_with_auth_code(tenant_id, client_id, client_secret, code, redirect_url)
        if 'access_token' in token:
            add_token_to_cache(client_id, tenant_id, token)
            return Response(json.dumps({'status': 'ok', 'message': 'token acquired'}), content_type='application/json')
        else:
            raise ValueError("token response malformed")

@app.route('/planner_tasks', methods=['GET', 'POST'])
@log_request
def list_all_tasks():
    if request.args.get('auth') and request.args.get('auth') == 'user':
        init_dao_on_behalf_on(client_id, client_secret, tenant_id, username, password)
    else:
        init_dao(client_id, client_secret, tenant_id)
    return Response(stream_as_json(get_tasks(get_plans(get_all_objects('/groups/')))), content_type='application/json')

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