import logging
import request
from plans_nd_tasks import get_tasks_for_plan, RESOURCE_PATH
from  dao_helper import GRAPH_URL


class CreateTasks():
    """docstring for CreateTasks."""

    def __init__(self):
        self.titles = {}
        self.response= ""


    def unique_title(title,plan_id):
        if not title in self.titles.get(plan_id):
            return True
        else:
            return False

    def populate_titles(plan_id):
        if not plan_id in self.titles:
            a=get_tasks_for_plan(plan_id)
            for plan in a:
                self.titles.append(plan["title"])

    def update_title_list(title):
        self.titles.append[title]

        # if no new title may be created, return False
    def try_create_uniqe_title(title):
        if valid_title(title):
            for i in range (1,20):
                new_title=title+"_"+str(i)
                if unique_title(new_title):
                    return new_title
            return False
        else:
            return False

    def valid_title(title):
        if "_" == title[-2:][0]:
            logging.warning("title has _ at end, no new postfix will be added")
            return False
        else:
            return True


    def post_task(task_data):
        update_title_list(task_data.get("title"))
        make_request(f'{GRAPH_URL}{RESOURCE_PATH}', 'POST', task_data)

    def append_response(response):
        self.response += "\tResult: " + response

    def valid_task(tasks_data):
        """
         Function to check if the task has the required data fields for creation.
         Required fields: PlanId, warning if tittle is missing
         """
        if not tasks_data.get('planId'):
            logging.error("Couldn't find planId, required field")
            return (False)
        if not tasks_data.get("title"):
            logging.warning("No title given for Task")
        return True

    def post_tasks(task_data_list):
            for task_data in task_data_list:
                if self.valid_task(task_data):
                    self.populate_titles(task_data.get("planId"))

                    if self.unique_title(task_data.get("title"),task_data.get("planId")):
                        self.post_task(task_data)
                    else:
                        new_title = self.try_create_uniqe_title(task_data.get("title"))
                        if new_title:
                            self.post_task(task_data)

                        else:
                            self.append_response("no unique title for tasks")

                else:
                    self.append_response("missing planId")
            return self.response
