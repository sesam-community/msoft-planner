import requests


from dao_helper import get_all_objects, get_object
import logging
import json
from dao_helper import get_all_objects, get_object,make_request,GRAPH_URL
from createplannerobjects import CreatePlannerTasks, CreatePlannerPlans

RESOURCE_PATH = "/planner/tasks/"
logging = logging.getLogger('microsoftplanner-connector.plans_nd_tasks')



def get_plans(group_generator_func):
    for group in group_generator_func:
        for plan in get_plans_for_group(group['id']):
            plan['details'] = get_plan_details(group['id'], plan['id'])
            plan['group_id'] = group['id']
            yield (plan)

def get_conversations(group_generator_func):
    for group in group_generator_func:
        for conversation in get_conversations_for_group(group['id']):
            conversation['details'] = get_conversation_details(group['id'], conversation['id'])
            conversation['group_id'] = group['id']
            yield (conversation)


def get_threads(conversation_generator_func):
    for conversation in conversation_generator_func:
        for task in get_threads_for_conversation(conversation['group_id'],conversation['id']):
            task['details'] = get_thread_details(conversation['group_id'],conversation['id'],task['id'])
            task['group_id'] = conversation['group_id']
            yield task

def get_posts(conversation_generator_func):
    for thread in conversation_generator_func:
        for post in get_posts_for_thread(thread['group_id'],thread['id']):
            post['details'] = get_post_details(thread['group_id'],thread['id'],post['id'])
            yield post

def get_tasks(plan_generator_func):
    for plan in plan_generator_func:
        for task in get_tasks_for_plan(plan['id']):
            task['details'] = get_task_details(task['id'])
            yield task

def get_tasks_for_plan(plan_id):
    yield from get_all_objects(f'/planner/plans/{plan_id}/tasks')

def get_plans_for_group(group_id):
    try:
        yield from get_all_objects(f'/groups/{group_id}/planner/plans')
    except requests.exceptions.HTTPError:
        # already logged in make_request function, no action needed
        pass

def get_conversations_for_group(group_id):
    try:
        yield from get_all_objects(f'/groups/{group_id}/conversations')
    except requests.exceptions.HTTPError:
        # already logged in make_request function, no action needed
        pass

def get_threads_for_conversation(group_id, conversation_id):
    try:
        yield from get_all_objects(f'/groups/{group_id}/conversations/{conversation_id}/threads')
    except requests.exceptions.HTTPError:
        # already logged in make_request function, no action needed
        pass

def get_posts_for_thread(group_id, thread):
    try:
        yield from get_all_objects(f'/groups/{group_id}/threads/{thread}/posts')
    except requests.exceptions.HTTPError:
        # already logged in make_request function, no action needed
        pass


def get_plan_details(group_id, plan_id):
    return get_object(f'/groups/{group_id}/planner/plans/{plan_id}/details')

def get_conversation_details(group_id, id):
    return get_object(f'/groups/{group_id}/conversations/{id}')

def get_post_details(group_id, thread, id):
    return get_object(f'/groups/{group_id}/threads/{thread}/posts/{id}')

def get_thread_details(group_id, conversation_id, thread_id):
    return get_object(f'/groups/{group_id}/conversations/{conversation_id}/threads/{thread_id}')

def get_task_details(task_id):
    try:
        return get_object(f'/planner/tasks/{task_id}/details')
    except Exception as e:
        return "Access denied..."

def create_plans(plan_data :list):
    CP = CreatePlannerPlans()
    return CP.create_plan(plan_data)

def create_tasks(task_data_list):
    """
    Function to create Planner tasks given as a list. Will post Tasks indivudially before returning response
    :param task_data: json object with group details, must contain plan identifier
    :param task_data: {title:string, percentComplete:int, dueDate:dateTimeTimeZone, assigneePriority: string, bucketId:string}
    :return: string
    Arbitrairy max number of tasks with same name set at 20. change range if needed
    """
    CT = CreatePlannerTasks()
    return CT.create_object(task_data_list)

def update_tasks(task_data_list):
    """
    Excpects a list of dicts [{id: <id>, task_data:{<task_data_dixt>}}]
    :param id: the id of the task in planner
    :param task_update_data: {@odata.etag:string, title:string, percentComplete:int, dueDate:dateTimeTimeZone, assigneePriority: string, bucketId:string}
    """
    for task_data in task_data_list:
        response = check_update_tasks_data(task_data)
        if response == "ok":
            task_id = task_data.get('id')
            make_request(f'{GRAPH_URL}{RESOURCE_PATH}{task_id}', 'PATCH',task_data)

    return response

def check_update_tasks_data(tasks_data):
    """
     Function to check that all required fields are populated
     required fields: '@odata.etag'
     """
    if tasks_data.get("@odata.etag") and tasks_data.get("id"):
        return "ok"

    else:
        return (f"Missing required field @odata.etag ={tasks_data.get('@odata.etag')} id = {tasks_data.get('id')} ")