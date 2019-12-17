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
    CT = CreateTasks()
    return CT.create_tasks(task_data_list)

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

class CreateTasks():
    """
    Created new functions to handle creation of tasks.
    Check that it has an unique title before posting new task.
    Returns Result for each creation of task when all is posted.
    """

    def __init__(self):
        self.titles = {}
        self.response= ""


    def unique_title(self,title,plan_id):
        if not title in self.titles.get(plan_id):
            return True
        else:
            return False

    def populate_titles(self,plan_id):
        """
         add all titles of tasks under the given plan_id
         if plan_id exist in dictonary skip
        """
        if not plan_id in self.titles:
            a=get_tasks_for_plan(plan_id)
            self.titles[plan_id]=[]
            for plan in a:
                self.titles[plan_id].append(plan["title"])

    def update_title(self,title,plan_id):
        """
        append title to dictonary under the given plan_id
        """
        self.titles[plan_id].append(title)


    def try_create_uniqe_title(self,title,plan_id):
        """
        add _nr at end of title, max nr set at 20
        if no new title may be created, return False
        """
        if self.valid_title(title):
            for i in range (1,20):
                new_title=title+"_"+str(i)
                if self.unique_title(new_title,plan_id):
                    return new_title
            return False
        else:
            return False

    def valid_title(self,title):
        if "_" == title[-2:][0]:
            logging.warning("title has _ at end, no new postfix will be added")
            return False
        else:
            return True


    def post_task(self,task_data):
        """
        create task by posting the task_data to GRAPH
        make_request will handle errors
        """
        try:
            self.update_title(task_data["title"],task_data["planId"])
            make_request(f'{GRAPH_URL}{RESOURCE_PATH}', 'POST', task_data)
            self.append_response("Ok")
        except:
            self.append_response("Error")
            pass

    def append_response(self,response):
        self.response += "\tResult: " + response

    def valid_task(self,tasks_data):
        """
         Function to check if the task has the required data fields forß creation.
         Required fields: PlanId, warning if tittle is missing
         """
        if not tasks_data.get('planId'):
            logging.error("Couldn't find planId, required field")
            return (False)
        if not tasks_data.get("title"):
            logging.warning("No title given for Task")
        return True

    def create_tasks(self,task_data_list):
        """
        itterate over task_data, performe check for validity and add response of each post
        """
        for task_data in task_data_list:
            if self.valid_task(task_data):
                self.populate_titles(task_data.get("planId"))

                if self.unique_title(task_data.get("title"),task_data.get("planId")):
                    self.post_task(task_data)
                else:
                    new_title = self.try_create_uniqe_title(task_data.get("title"),task_data.get("planId"))
                    if new_title:
                        task_data["title"]= new_title
                        self.post_task(task_data)
                        self.append_response("Ok")
                    else:
                        self.append_response("no unique title for tasks")

            else:
                self.append_response("missing planId")
        return self.response
