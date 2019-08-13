from flask import Flask, request, jsonify, Response, session, redirect
import json
import datetime
import logging
import uuid
import os
from logger_helper import log_request
from auth_helper import get_authorize_url, get_token_with_auth_code, add_token_to_cache, get_token_on_behalf_of_user
from dao_helper import init_dao, get_all_objects, init_dao_on_behalf_on, stream_as_json
from plans_nd_tasks import get_plans, get_tasks
from planner_groups import get_all_groups
from planner_users import get_all_users

app = Flask(__name__)

os.environ['client_id'] = '67f967fb-c09e-4b06-a689-8865ac54ef5d'
os.environ['client_secret'] = 'zRkY_BlJA_Vdv--9YdBdNF5juxy6AaU2'
os.environ['tenant_id'] = '7bcbcc45-fb12-41d3-8ace-fa0fffaebf1d'
os.environ['username'] = 'jonas.christensen@sesam.io'
os.environ['password'] = 'Drummsoul7.89'
os.environ['redirect_url'] = 'http://localhost:5000/auth'
os.environ['token'] = 'Bearer eyJ0eXAiOiJKV1QiLCJub25jZSI6IjFvckpXTUhnN1d6Qkl4cUNmM2ZHVng1OVVCY3VTVXE3ZThEUWVuemxFWW8iLCJhbGciOiJSUzI1NiIsIng1dCI6InU0T2ZORlBId0VCb3NIanRyYXVPYlY4NExuWSIsImtpZCI6InU0T2ZORlBId0VCb3NIanRyYXVPYlY4NExuWSJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC83YmNiY2M0NS1mYjEyLTQxZDMtOGFjZS1mYTBmZmZhZWJmMWQvIiwiaWF0IjoxNTY1NjE5NzcyLCJuYmYiOjE1NjU2MTk3NzIsImV4cCI6MTU2NTYyMzY3MiwiYWNjdCI6MCwiYWNyIjoiMSIsImFpbyI6IkFWUUFxLzhNQUFBQXBwRkJGVzNYZGJ0QUFQejR5ZEd6V3kxaHRGMTVnVUhvZ2RzRWxRT0JNaUVSRU1ucDdwZjRudWliSC9zTTNTZlBCcDhKR2sxU2twSmpwL1UwengyUzZxMGVwSzVIOUtTV3lOUW5OOXAzeXUwPSIsImFtciI6WyJwd2QiLCJtZmEiXSwiYXBwX2Rpc3BsYXluYW1lIjoiUGxhbm5lckNvbm5lY3RvciIsImFwcGlkIjoiNjdmOTY3ZmItYzA5ZS00YjA2LWE2ODktODg2NWFjNTRlZjVkIiwiYXBwaWRhY3IiOiIxIiwiaXBhZGRyIjoiMTg1LjEzLjkyLjI0IiwibmFtZSI6IkpvbmFzIEFscyBDaHJpc3RlbnNlbiIsIm9pZCI6ImY3M2Q3ZDU5LTczMTAtNDE2MS1hM2FlLTdmMjNlMzJiZDBhZiIsInBsYXRmIjoiNSIsInB1aWQiOiIxMDAzMjAwMDRCNDkzMzNDIiwic2NwIjoiRGlyZWN0b3J5LlJlYWRXcml0ZS5BbGwgR3JvdXAuUmVhZC5BbGwgR3JvdXAuUmVhZFdyaXRlLkFsbCBUYXNrcy5SZWFkIFRhc2tzLlJlYWQuU2hhcmVkIFVzZXIuUmVhZCBwcm9maWxlIG9wZW5pZCBlbWFpbCIsInNpZ25pbl9zdGF0ZSI6WyJpbmtub3dubnR3ayIsImttc2kiXSwic3ViIjoiSk11dkxTb3pkQVBiZUM4STMyeUZDMDJIaWVyU0FXZlIxVngxVnZPWkprbyIsInRpZCI6IjdiY2JjYzQ1LWZiMTItNDFkMy04YWNlLWZhMGZmZmFlYmYxZCIsInVuaXF1ZV9uYW1lIjoiam9uYXMuY2hyaXN0ZW5zZW5Ac2VzYW0uaW8iLCJ1cG4iOiJqb25hcy5jaHJpc3RlbnNlbkBzZXNhbS5pbyIsInV0aSI6ImNOcEh2MHdPWUVxZHJseXpodTllQUEiLCJ2ZXIiOiIxLjAiLCJ4bXNfc3QiOnsic3ViIjoicGNnYk1OZFlKRlpYWG9qNWxXTFhVM0RYSVUwaW4wYzBsdFBtdC1WamJDYyJ9LCJ4bXNfdGNkdCI6MTU0MzQwMTgxOX0.NAMbsTWTFbMu1R6AQHe1eReBygwD0k1_rbDo4k25Gkamwui6y4C56syGKWjjFBlaKOfryzhQpGTq_g8XI4tzK-U7L-DIn0aqtXNoWGWl77PD9ACQT9TOviWT_R4atcozAqY8zknrz3DolqbtU89I-MhunXL8qoScT5ELuBnQT8PwjcsHktbn0BNfHlvVJHMc3-AuLLoO6p0PDHMWQfrO0-OJDH9C6BmSmxeiG7oz_IcVM4KELthmAhaZJHbvsRGYgl7_HsNN7Ts1tof9ULaZLcfhEaslUaWAGv64g7hdwK7AIM52pAZE7heJEQQKBiVF9oUBBlcLu7huz6J9WpCrpA'
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
            return Response(json.dumps({'status': 'Created token for the graph API', 'to do': 'Copy the below line and paste in your sesam system config to set token env variable', 'token': f"$ENV({token['access_token']})"}), content_type='application/json')
        else:
            raise ValueError("token response malformed")

@app.route('/planner/<var>', methods=['GET', 'POST'])
@log_request
def list_all_tasks(var):
    if request.args.get('auth') and request.args.get('auth') == 'user':
        init_dao_on_behalf_on(client_id, client_secret, tenant_id, username, password)
    else:
        init_dao(client_id, client_secret, tenant_id)
        if var.lower() == "tasks":
            return Response(stream_as_json(get_tasks(get_plans(get_all_objects('/groups/')))), content_type='application/json')
        elif var.lower() == "plans":
            return Response(stream_as_json(get_plans(get_all_objects('/groups/'))), request.args.get('since'), content_type='application/json')
        elif var.lower() == "groups":
            return Response(get_all_groups(request.args.get('since')), content_type='application/json')
        elif var.lower() == "users":
            return Response(get_all_users(request.args.get('since')), content_type='application/json')
        else:
            return Response(json.dumps({"You need to choose one of the following vals in the '/planner/'path" : 'tasks or plans'}), content_type='application/json')

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