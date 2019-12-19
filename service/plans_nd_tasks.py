import requests
import logging
import json
from dao_helper import get_all_objects, get_object,make_request,GRAPH_URL
from createplannerobjects import CreatePlannerTasks

logging = logging.getLogger('microsoftplanner-connector.plans_nd_tasks')


def get_plans(group_generator_func):
    for group in group_generator_func:
        for plan in get_plans_for_group(group['id']):
            plan['details'] = get_plan_details(plan['id'])
            yield (plan)


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
        # already   logged in make_request function, no action needed
        pass


def get_plan_details(plan_id):
    return get_object(f'/planner/plans/{plan_id}/details')


def get_task_details(task_id):
    return get_object(f'/planner/tasks/{task_id}/details')




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
    try:
        for task_data in task_data_list:
            response = check_update_tasks_data(task_data.get("task_data"))
            if response == "ok":
                task_id = task_data.get('id')
                make_request(f'{GRAPH_URL}{RESOURCE_PATH}{task_id}', 'PATCH',task_data["task_data"])
    except Exception as e:
        response = f"failed with error : {e}"
        logging.info("failed to update task, id: ", task_data.get('id'))

    return response

def check_update_tasks_data(tasks_data):
    """
     Function to check that all required fields are populated
     required fields: '@odata.etag'
     """
    if tasks_data.get("@odata.etag"):
        return "ok"

    else:
        return "Missing required field @odata.etag"
