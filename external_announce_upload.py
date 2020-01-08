import re
from locust import HttpLocust, TaskSet, task, between
from urllib.parse import unquote
from requests_toolbelt import MultipartEncoder


class WebsiteTasks(TaskSet):
    csrf_token = ''

    def on_start(self):
        # get a XSRF-TOKEN
        response = self.client.get('/moe/public/login/')
        self.csrf_token = re.search(
            'meta name="csrf-token" content="(.+?)"', response.text).group(1)

    @task()
    def add_new_external_announce(self):
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

        # go to external announce page
        with self.client.get('/moe/public/eFound/managMoe/externalAnnounce',
                             catch_response=True) as response:
            if response.status_code == 200:
                response.success()

        # add new external announce
        # 用 MultipartEncoder 方便發送具有 webkit boundary 的 multipart/form-data
        encoder = MultipartEncoder(fields={'_token': self.csrf_token,
                                           'FrontAnnouncement_Input_Title': 'Request From Locust',
                                           'FrontAnnouncement_Input_KindObject': '0',
                                           'FrontAnnouncement_Input_Date1': '2020-01-01',
                                           'FrontAnnouncement_Input_Date2': '2020-01-31',
                                           'FrontAnnouncement_Texterea_Content': 'Testing',
                                           'FrontAnnouncement_Input_Status': '1',
                                           'FrontAnnouncement_Input_File': ('test.pdf', open('/Users/shenglin-alex/Workspace/LocustStarter/test_files/test.pdf', 'rb'), 'application/pdf')})
        headers = {'Content-Type': encoder.content_type,
                   'X-XSRF-TOKEN': unquote(self.locust.client.cookies['XSRF-TOKEN'])}
        with self.client.post('/moe/public/eFound/managMoe/externalAnnounce/add',
                              catch_response=True,
                              data=encoder,
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
    host = 'http://140.124.39.132'
    wait_time = between(1.0, 5.0)
