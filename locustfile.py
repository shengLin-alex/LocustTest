from locust import HttpLocust, TaskSet, task, between
from urllib.parse import unquote


class WebsiteTasks(TaskSet):
    xsrf_token = ''
    cookieJar = {}

    def on_start(self):
        with self.client.get("/moe/public/login/",
                             catch_response=True) as response:
            self.cookieJar = response.cookies
            self.xsrf_token = unquote(response.cookies["XSRF-TOKEN"])

    @task(1)
    def login(self):
        headers = {"content-type": "multipart/form-data",
                   "X-XSRF-TOKEN": self.xsrf_token}
        payload = {"account": "admin", "password": "123456"}

        # login
        with self.client.post("/moe/public/eFound/login",
                              catch_response=True,
                              data=payload,
                              headers=headers,
                              cookies=self.cookieJar) as response:
            self.cookieJar = response.cookies

        # logout
        headers = {"X-XSRF-TOKEN": self.xsrf_token}
        with self.client.delete("/moe/public/logout",
                                catch_response=True,
                                headers=headers,
                                cookies=self.cookieJar) as response:
            self.cookieJar = response.cookies

    # @task(2)
    # def get_external_announce(self):
    #     with self.client.get("/moe/public/eFound/managMoe/externalAnnounce/",
    #                          catch_response=True,
    #                          cookies=self.cookieJar) as response:
    #         if response.status_code != 200:
    #             response.failure("Auth not pass!")
    #         else:
    #             response.success()


class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    host = "http://140.124.39.132"
    wait_time = between(1.0, 5.0)
