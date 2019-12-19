import logging
from  dao_helper import GRAPH_URL,get_all_objects, make_request

logging = logging.getLogger('microsoftplanner-connector.CreatePlannerObject')
 ### buckets uses name else identical classes
class CreatePlannerTasks():
    """
    Class to check if PlannerObjects have the required fields before posting to Planner API
    Check that it has an unique title before posting.
    Returns Result for each creation of objects in Response
    tasks uses sends data with title, buckets uses name
    """

    def __init__(self):
        self.titles = {}
        self.response= ""
        self.RESOURCE_PATH = "/planner/tasks/"


    def _get_objects_in_plan_generator(self,plan_id):
            yield from get_all_objects(f'/planner/plans/{plan_id}/tasks')


    def unique_title(self,title=None,plan_id=None):
        if not title in self.titles.get(plan_id):
            return True
        else:
            return False

    def populate_titles(self,plan_id):
        """
         add all titles/name of object under the given plan_id
         if plan_id exist in dictonary skip
        """
        if not plan_id in self.titles:
            try:
                a=self._get_objects_in_plan_generator(plan_id)
                self.titles[plan_id]=[]
                for plan in a:
                    self.titles[plan_id].append(plan["title"])
            except:
                logging.warning(f"could not get existing tasks from planId: {plan_id}")
                print("warning")
                self.titles[plan_id]=[]


    def update_title(self,title=None,plan_id=None):
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


    def post_object(self,object_data):
        """
        create task by posting the task_data to GRAPH
        make_request will handle errors
        """
        try:
            self.update_title(title=object_data["title"],plan_id=object_data["planId"])
            make_request(f'{GRAPH_URL}{ self.RESOURCE_PATH}', 'POST', object_data)
            logging.info(f'Created task with title {object_data.get("title")}')
            self.append_response("Ok")
            return True
        except:
            self.append_response("Error")
            return False

    def append_response(self,response):
        self.response += "\tResult: " + response

    def valid_object(self,object_data):
        """
         Function to check if the task has the required data fields for creation.
         Required fields: PlanId, warning if tittle is missing
         """
        if not object_data.get('planId'):
            logging.error("Couldn't find planId, required field")
            self.append_response("missing planId")
            return (False)
        if not object_data.get("title"):
            logging.warning("No title set for task")
        return True

    def create_object(self,object_data_list):
        """
        itterate over task_data, performe check for validity and add response of each post
        """
        for object_data in object_data_list:
            if self.valid_object(object_data):
                self.populate_titles(object_data.get("planId"))

                if self.unique_title(title=object_data.get("title"),plan_id=object_data.get("planId")):
                    self.post_object(object_data)
                else:
                    new_title = self.try_create_uniqe_title(object_data.get("title"),object_data.get("planId"))
                    if new_title:
                        object_data["title"]= new_title
                        self.post_object(object_data)
                    else:
                        logging.error(f'no unique title for Task')
                        self.append_response(f'no unique title for task')
            else:
                pass
        return self.response


class CreatePlannerBuckets():
    """
    Class to check if PlannerObjects have the required fields before posting to Planner API
    Check that it has an unique name before posting.
    Returns Result for each creation of objects in Response
    tasks uses sends data with title, buckets uses name
    """

    def __init__(self):
        self.names = {}
        self.response= ""





    def _get_objects_in_plan_generator(self,plan_id):
            yield from get_all_objects(f'/planner/plans/{plan_id}/buckets')




    def unique_name(self,name=None,plan_id=None):
        if not name in self.names.get(plan_id):
            return True
        else:
            return False

    def populate_names(self,plan_id):
        """
         add all names of object under the given plan_id
         if plan_id exist in dictonary skip
        """
        if not plan_id in self.names:
            try:
                a=self._get_objects_in_plan_generator(plan_id)
                self.names[plan_id]=[]
                for plan in a:
                    self.names[plan_id].append(plan["name"])
            except:
                logging.warning(f"could not get existing buckets from planId: {plan_id}")
                self.names[plan_id]=[]


    def update_name(self,name=None,plan_id=None):
        """
        append name to dictonary under the given plan_id
        """
        self.names[plan_id].append(name)



    def try_create_uniqe_name(self,name=None,plan_id=None):
        """
        add _nr at end of name, max nr set at 20
        if no new name may be created, return False
        """
        if self.valid_name(name):
            for i in range (1,20):
                new_name=name+"_"+str(i)
                if self.unique_name(name=new_name,plan_id=plan_id):
                    return new_name
            return False
        else:
            return False

    def valid_name(self,name):
        if "_" == name[-2:][0]:
            logging.warning("name has _ at end, no new postfix will be added")
            return False
        else:
            return True


    def post_object(self,object_data):
        """
        create task by posting the task_data to GRAPH
        make_request will handle errors
        """
        try:
            self.update_name(name=object_data["name"],plan_id=object_data["planId"])
            make_request(f'{GRAPH_URL}/planner/buckets', 'POST', object_data)
            logging.info(f'Created bucket with name {object_data.get("name")}')
            self.append_response("Ok")
            return True
        except:
            self.append_response("Error")
            return False

    def append_response(self,response):
        self.response += "\tResult: " + response

    def valid_object(self,object_data):
        """
         Function to check if the task has the required data fields for creation.
         Required fields: PlanId, warning if tittle is missing
         """
        if not object_data.get('planId'):
            logging.error("Couldn't find planId, required field")
            self.append_response("missing planId")
            return False
        if not object_data.get("name"):
            logging.warning("No name set for bucket")
        return True

    def create_object(self,object_data_list):
        """
        itterate over task_data, performe check for validity and add response of each post
        """
        for object_data in object_data_list:
            if self.valid_object(object_data):
                self.populate_names(object_data.get("planId"))

                if self.unique_name(name=object_data.get("name"),plan_id=object_data.get("planId")):
                    self.post_object(object_data)
                else:
                    new_name = self.try_create_uniqe_name(object_data.get("name"),object_data.get("planId"))
                    if new_name:
                        object_data["name"]= new_name
                        self.post_object(object_data)
                    else:
                        logging.error(f'no unique name for bucket')
                        self.append_response(f'no unique name for bucket')
        return self.response
