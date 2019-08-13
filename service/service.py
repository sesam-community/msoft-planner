from flask import Flask, request, jsonify, Response, session, redirect
import json
import datetime
import logging
import uuid
import os
from logger_helper import log_request
from auth_helper import get_authorize_url, get_token_with_auth_code, add_token_to_cache, get_token_on_behalf_of_user, check_if_token_exist_in_env
from dao_helper import init_dao, get_all_objects, init_dao_on_behalf_on, stream_as_json
from plans_nd_tasks import get_plans, get_tasks
from planner_groups import get_all_groups
from planner_users import get_all_users
from planner_buckets import get_all_buckets, get_buckets

app = Flask(__name__)

env = os.environ.get

client_id = env('client_id')
client_secret = env('client_secret')
tenant_id = env('tenant_id')
username = env('username')
password = env('password')
redirect_url = env('redirect_url')
env_access_token = env('access_token')

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
    app.logger.info("Microsoft Planner Service running on /auth port as expected")
    state = str(datetime.datetime.now().timestamp()) if 'state' not in session else session['state']
    token = dict()
    if not request.args.get('code'):
        session['state'] = state
        return redirect(get_authorize_url(tenant_id, client_id, state, redirect_url))
    else:
        code = request.args.get('code')
        returned_state = request.args.get('state')
        if state != returned_state:
            print(state)
            print(returned_state)
            app.logger.error("Remove the query parameters after the '/auth' to make sure request and response state remains the same")
            raise SystemError("Response state doesn't match request state")
        
        if env_access_token is not None:
            app.logger.info('Using env access token')
            token = check_if_token_exist_in_env(token, env_access_token)
        if len(token) == 0:
            app.logger.info('Generating new access token')
            token = get_token_with_auth_code(tenant_id, client_id, client_secret, code, redirect_url)
        if 'access_token' in token:
            app.logger.info('Adding access token to cache...')
            add_token_to_cache(client_id, tenant_id, token)
            return Response(json.dumps({'status': 'Created token for the graph API', 'to do': 'Copy the below line and paste in your sesam system config to set token env variable', 'access_token': f"$ENV({token['access_token']})"}), content_type='application/json')
        else:
            app.logger.info("token response malformed")

@app.route('/planner/<var>', methods=['GET', 'POST'])
@log_request
def list_all_tasks(var):
    if request.args.get('auth') and request.args.get('auth') == 'user':
        init_dao_on_behalf_on(client_id, client_secret, tenant_id, username, password)
    else:
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