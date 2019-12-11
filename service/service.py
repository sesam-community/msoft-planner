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

os.environ['client_id'] = 'ab48bf45-add0-4e84-a51d-1427bff399e4'
os.environ['client_secret'] = 'HIXudOOp9xD0kScqM=PfUpwJm1Y_[A_9'
os.environ['tenant_id'] = 'f2716ff5-b2ec-46c4-a1e7-fa482bf4b365'
os.environ['refresh_token'] = 'AQABAAAAAACQN9QBRU3jT6bcBQLZNUj7srP2LYIQRTS58xx9oFzFv83onInJUUan_clJRm_mLNLKEZzj2wgh1VKpzaJ5XLpLVrTcneWV_gE2U2cf_64jdP4SDtLYaOQ_T0BIlMWQr85hVmbOfsxUfaNwPTdqsxenr2VpScj44d6VRgv6CZR1cIagolDX1qpdFdW9r4hXhKMSQNnseVyRumF7_N6OiU-4UrXfELhMtcMEZdpHpgwPfE2qsSOOs9lIcAHpAklzLNJAdpVjPPRxdr6WVFRa269E0Fxi6pQ6Yro3G81SNGIfjA6LH5jbbK2dIWWhz3w9R8_N4A8UnhZS8pGcxwWbfyZMro6_jQTr6e-LkK2E8HlcmEzRP-Mq1nOgqthfb59bTjACRKql6kHcB4cZr3dKBh_bQw9BJbn4MPqOkr9-ObYFeamxib2oRekg4UdCg9-M0mp-Hdxd1AN8uCWvQlGU9j3uLeAtxTNWFOGPNH4VisZlgRNaJ550xTzy3ENUmO8xLvDtBPvBuGg-J1r_Fe_RmWsdjxqA0w2qcE6vY9ad1_kWCc4MS4VAqArKMf1ythtI-ef6sUCnTqvX6dSIyYAe0ZnEQ2EirUnqSgWhi1uKUiOxJwWQ4yBRxHYkjcPkpPD1WinIyV0Z9p7narYkYIpmmNkZuXCeLWHXaZipP0xcQq-WkPkNWve4ToYfnTDKbItcNmXK8zRUUHylEOXHYi4GzOq2nSCT1Wyn6n_dvwrNNa0nWrAuKV4ObpSxVkdKU7uDxbvVDm8zjjXrXMePAiJ2VrNmdZ1aP74W3hJeQX_9hMfXidJCIjfKFwa02ygBIlnE0TMgAA'

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
    print("start auth_user")
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
            print("returned token: \t", token)
            request_count = 1
        if 'access_token' in token:
            app.logger.info('Adding access token to cache...')
            add_token_to_cache(client_id, tenant_id, token)
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
        return Response(stream_as_json(create_tasks()), content_type='application/json')
    elif var.lower() == "update_tasks":
        app.logger.info(f'Requesting {var} from the graph API')
        return Response(stream_as_json(update_tasks()), content_type='application/json')

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
