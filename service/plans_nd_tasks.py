import requests

from dao_helper import get_all_objects, get_object,make_request,GRAPH_URL
RESOURCE_PATH = '/planner/tasks'

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
        # already logged in make_request function, no action needed
        pass

def create_tasks():
    #   "planId": "Py6LMdklhES5PgCK4xyUcpcAHrQT",
    #   "bucketId": "21xu56a4ykSdmaVjflkl75cAOedV",
    test_task={"planId":"Py6LMdklhES5PgCK4xyUcpcAHrQT","title":"task from func","bucketId":"21xu56a4ykSdmaVjflkl75cAOedV"}
    make_request(f'{GRAPH_URL}{RESOURCE_PATH}', 'POST', test_task)
    print("created task")

def update_tasks():
    taskId = "/rS8Ai524w0OGESACOjSKd5cAI75N"
    etag= "W/\"JzEtVGFzayAgQEBAQEBAQEBAQEBAQEBASCc=\""
    #   "bucketId": "21xu56a4ykSdmaVjflkl75cAOedV",
    print("try to update the created task")
    update_task_data={"title":"updated title2","percentComplete":95,"@odata.etag":etag}
    print("requeset made: \t",update_task_data)
    make_request(f'{GRAPH_URL}{RESOURCE_PATH}{taskId}', 'PATCH',update_task_data)
    print("sucsessfully updated task")


def get_plan_details(plan_id):
    return get_object(f'/planner/plans/{plan_id}/details')


def get_task_details(task_id):
    return get_object(f'/planner/tasks/{task_id}/details')
