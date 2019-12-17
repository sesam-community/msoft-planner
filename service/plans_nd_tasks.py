import requests
import logging
import json
from dao_helper import get_all_objects, get_object,make_request,GRAPH_URL

RESOURCE_PATH = "/planner/tasks/"

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
    Function to create a task
    :param task_data: json object with group details, must contain plan identifier
    :param task_data: {title:string, percentComplete:int, dueDate:dateTimeTimeZone, assigneePriority: string, bucketId:string}
    :return: string
    Arbitrairy max number of tasks with same name set at 20. change range if needed
    """
    response = ""
    request_made = False
    try:
        title_dict = {} # dictoranry with all planId and corosponding titles
        for task_data in task_data_list:
            request_made = False
            # if task_data is not valid, logg error in check_create_task_data
            if check_create_tasks_data(task_data):
                #update title_dict to include new planId
                if not task_data["planId"] in title_dict:
                    title_dict[task_data["planId"]] = get_all_titles(task_data["planId"])

                    #check if title exist in the plan if it does add a <_int> at the end max value 100
                if task_data.get("title") in title_dict[task_data["planId"]]:
                    logging.info("title already exist in plan, adding _numerator at end")
                    for i in range(1,20):
                        if (task_data.get("title")+"_"+str(i)) in title_dict[task_data["planId"]]:
                            pass
                        else:
                            request_made=True
                            task_data["title"] = task_data["title"] + "_" + str(i)
                            title_dict[task_data["planId"]].append(task_data["title"])
                            make_request(f'{GRAPH_URL}{RESOURCE_PATH}', 'POST', task_data)
                            logging.info("created new task, title  : ", task_data['title'])
                            break


                else:
                    request_made = True
                    make_request(f'{GRAPH_URL}{RESOURCE_PATH}', 'POST', task_data)
                    logging.info("created new task, title  : ", task_data['title'])
                    title_dict[task_data["planId"]].append(task_data["title"])
                    response = "ok"
            if not request_made:
                logging.info("failed to create new task, title  : ", task_data['title'])
                response += "failed "
            else:
                response += "ok "

    except Exception as e:
        response = f"failed with error : {e}"
        logging.info("failed to create new task, title  : ", task_data['title'])

    return response

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


def check_create_tasks_data(tasks_data):
    """
     Function to check if valid data for creation of task
    required fields: PlanId, warning if tittle is missing
     """
    if not tasks_data.get('planId'):
        logging.error("Couldn't find planId, required field")
        return (False)
    if not tasks_data.get("title"):
        logging.warning("No title given for Task")

    return True


def check_update_tasks_data(tasks_data):
    """
     Function to check that all required fields are populated
     required fields: '@odata.etag'
     """
    if tasks_data.get("@odata.etag"):
        return "ok"

    else:
        return "Missing required field @odata.etag"

def check_unique_title(title,plan_id, ):
    """
    :param title: title of the tasks to be created
    :param plan_id: plan id where the task will be created ( only needs to be uniquely named inside plan)
    :return: a list of titles in the plan
    """

    titles = get_all_titles(plan_id)
    return titles

def get_all_titles(plan_id):
    """
    :param plan_id:
    :return: a list of all titles in the specified plan
    """
    title = []
    a=get_tasks_for_plan(plan_id)
    for plan in a:
        title.append(plan["title"])
    return title