from flask import Flask, request, jsonify, Response, session, redirect, render_template
import json
import datetime
import adal
from datetime import timedelta
import webbrowser
import logging
import requests
import uuid
import os
from logger_helper import log_request
from auth_helper import add_token_to_cache, get_tokens_as_app, sign_in_redirect_as_app
from dao_helper import init_dao, get_all_objects, stream_as_json
from plans_nd_tasks import get_plans, get_tasks, create_tasks,update_tasks
from planner_groups import get_all_groups
from planner_users import get_all_users
from planner_buckets import get_all_buckets, get_buckets

app = Flask(__name__)

env = os.environ.get


client_id = env('client_id')
client_secret = env('client_secret')
tenant_id = env('tenant_id')
refresh_token = env('refresh_token')

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

    output = (f"{user_code_info.get('message')}")
    url = output[47:80]
    code = output[100:109]

    return render_template('index.html', url=url, code=code)


@app.route('/auth', methods=['POST', 'GET'])
@log_request
def auth_user():
    """
    Endpoint to sign in user interactively by using Microsoft login page
    :return:
    """
    global token
    app.logger.info("Microsoft Planner Service running on /auth port as expected")
    try:
        request_count = 0
        if request_count == 0:
            token = get_tokens_as_app(client_id, user_code_info, tenant_id)
            request_count = 1
        if 'access_token' in token:
            app.logger.info('Adding access token to cache...')
            (client_id, tenant_id, token)
            return_object = (f"{token['refresh_token']}")
            return render_template('token.html', return_object=return_object)
        else:
            return_error = ("Token response did not result in a proper response. Athenticate again please.")
            return render_template('token.html', return_error=return_error)
    except AttributeError or TypeError:
        return_error = ('Authentification failed. Please pull and restart your system and authenticate again.')
        return render_template('token.html', return_error=return_error)
    except adal.AdalError as err:
        return_error = ("You're logged in with the wrong user. Please log out and authenticate again.")
        return render_template('token.html', return_error=return_error)

@app.route('/planner/<var>', methods=['GET', 'POST','PATCH'])
@log_request
def list_all_tasks(var):
    """
    Endpoint for calling Graph API
    """
    init_dao(client_id, client_secret, tenant_id, refresh_token)

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
    elif var.lower() == "create_tasks":
        app.logger.info(f'Requesting {var} from the graph API')
        return create_tasks(stream_as_json(.get_json()))
    elif var.lower() == "update_tasks":
        app.logger.info(f'Requesting {var} from the graph API')
        return update_tasks(stream_as_json(request.get_json()))

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
