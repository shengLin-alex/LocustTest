import re
from locust import HttpLocust, TaskSet, task, between
from urllib.parse import unquote


class WebsiteTasks(TaskSet):
    csrf_token = ''

    def on_start(self):
        response = self.client.get('/moe/public/login/')
        self.csrf_token = re.search(
            'meta name="csrf-token" content="(.+?)"', response.text).group(1)

    @task()
    def login_and_logout(self):
        # login
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "X-XSRF-TOKEN": unquote(self.locust.client.cookies['XSRF-TOKEN'])}
        payload = {'_token': self.csrf_token,
                   'account': 'admin',
                   'password': '123456'}
        with self.client.post("/moe/public/eFound/login",
                              catch_response=True,
                              data=payload,
                              headers=headers) as response:
            if response.status_code == 200:
                response.success()

        # logout
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "X-XSRF-TOKEN": unquote(self.locust.client.cookies['XSRF-TOKEN'])}
        payload = {'_token': self.csrf_token,
                   '_method': 'DELETE'}
        with self.client.post("/moe/public/logout",
                              catch_response=True,
                              data=payload,
                              headers=headers) as response:
            if response.status_code == 200:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    host = "http://140.124.39.132"
    wait_time = between(1.0, 5.0)
