import pickle, time, os
from threading import Thread, Lock
from tools import log as logger, hash_, divide_message
from Globals import PATH
log = logger("task manager", "task_manager.log")

class Task:

    
    def __init__(self, *args):
        self.func    = args[0]
        self.sent = []

    def __call__(self, *args, **kwargs):
        data = args[0]
        projects = self.func( data )
        temp = []
        for project in projects:
            hs = project.hash()
            if hs not in self.sent:

                temp.append( str(project)  )
                self.sent.append( hs )
        return temp


class TaskManager:
    def __init__(self, *args, **kwargs):
        self.get_data = args[0]
        self.message_queue = args[1]
        self.lock = Lock()
        self.users = self.load_state()
        self.wait = 120

    def __getitem__(self, key):
        try:
            return self.users[key]
        except KeyError:
            return None

    def save_state(self):
        absolute = os.path.join(PATH, "state")
        with open(absolute, "wb") as f:
            pickle.dump(self.users, f)

    def load_state(self):
        try:
            absolute = os.path.join(PATH, "state")
            with open(absolute, "rb") as f:
                data = pickle.load(f)
            return data
        except FileNotFoundError as E:
            return {}


    def __setitem__(self, key, value):
        with self.lock:
            if key not in self.users:
                self.users[key] = {}
                self.users[key][1] = value
            else:
                num = max(self.users[key].keys()) + 1
                self.users[key][num] = value
            self.save_state()

    def remove(self, user_id, task_id):
        status = 0
        user = self.users[user_id]

        if user:
            with self.lock:
                if task_id in user:
                    del user[ task_id ]
                    status = 1
                self.save_state()
        return status

    def clear_task(self, user_id, admin = None):
        user = self.users[ user_id ]
        status = 0

        if user:
            with self.lock:
                self.users[ user_id ] = {}
                status = 1
                self.save_state()

        return status

    def perform_task(self):
        log.info("perform_task init")
        while True:
            with self.lock:
                users = self.users
                log.info("Users: %s", self.users)
                # insert here data
                data = self.get_data()
                for user_id in users:
                    for task_id, task in users[user_id].items():
                        # log.info("run task")
                        messages = task(data)
                        # import pdb;pdb.set_trace()
                        if messages:
                            self.message_queue.put( ( user_id, messages ) )
                self.save_state()
            time.sleep( self.wait )

    def run(self):
        Thread( target=self.perform_task, daemon=True ).start()