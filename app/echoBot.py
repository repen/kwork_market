import requests, time, pickle
from tools import log as logger, divide_message
from Model import get_projects
from queue import Queue
from threading import Thread
from taskManager import TaskManager, Task
from Globals import TOKEN

message_queue = Queue()

log = logger("echoBot", "echoBot.log")


def func1(data):
    ll = []
    for project in data:
        ll.append( project )
    return ll



data_manager = get_projects
task_manager = TaskManager( data_manager, message_queue )
task_manager.run()

class Telegram:

    def __init__(self, token):
        self.token     = token
        self.update_id = None
        self.api_url   = "https://api.telegram.org/bot{}/".format(token)
        self.timeout   = 10

    def get_updates(self):
        while True:
            method = 'getUpdates'
            params = {'timeout': self.timeout, 'offset': self.update_id}
            try:
                resp = requests.get(self.api_url + method, params,timeout=self.timeout*2)
                message_list = resp.json()['result']
                return message_list
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as Er:
                log.error("Error connect %s. reconnect", Er)
                time.sleep(5)


    def get_update(self):
        while True:
            method = 'getUpdates'
            params = { 'timeout': self.timeout, 'offset': self.update_id }
            try:
                resp = requests.get(self.api_url + method, params, timeout=self.timeout*2)
                data = resp.json()

                if "result" in data.keys():
                    message_list = data['result']
                else:
                    raise StopIteration

                if message_list:
                    if self.update_id is None:
                        self.update_id = message_list[0]['update_id']
                    yield message_list[0]
                else:
                    raise StopIteration
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as Er:
                log.info("Error connect %s. reconnect", Er)
                time.sleep(5)


    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, "parse_mode" :"Markdown"}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp


    def _echo(self):

        for update in self.get_update():
            # log.info("Data: %s", update)
            # New logic

            # ==========
            self.update_id += 1
            if "text" in update['message'].keys():
                message = update['message']['text']
                chat = update['message']['from']['id']
                user_id = update['message']['from']['id']
                log.info("text = %s | chat_id = %d", message, chat)
                if message == "/kwork add":
                    # added task
                    task = Task( func1 )
                    task_manager[user_id] = task
                    log.info("/kwork add Task create")

                params = (chat, message)
                message_queue.put( params )
                # self.send_message( chat, message )
            else:
                log.info("Message no text. value: %s", update['message'])

    def serve_queue(self):
        # создать пулл потоков для обработки. 4 работника хватит =).
        while True:
            items = message_queue.get()
            chat_id = items[0]
            messages = items[1]
            if isinstance(messages, list):
                for message in messages:
                    log.info("Len message: %d", len(message))
                    self.send_message(chat_id, message)
            if isinstance(messages, str):
                log.info("Len message: %d", len(messages))
                self.send_message(chat_id, messages  )
            message_queue.task_done()

    def echo(self):
        log.info("Start echo bot")
        Thread(target=self.serve_queue, daemon=True).start()

        try:
            self.update_id = self.get_updates()[0]['update_id']
        except IndexError:
            pass

        while True:
            try:
                self._echo()
            except KeyboardInterrupt:
                log.info("Ctr + C (Break)")
                break

        log.info("Stop echo bot")


def main():
    bot = Telegram(TOKEN)
    bot.echo()

if __name__ == '__main__':
    main()