from locust import HttpLocust, TaskSet, task, between


class WebsiteTasks(TaskSet):
    cookieJar = {}

    def on_start(self):
        headers = {"content-type": "multipart/form-data"}
        payload = {"account": "admin", "password": "123456"}
        with self.client.post("/moe/public/eFound/login",
                              catch_response=True,
                              data=payload,
                              headers=headers) as response:
            self.cookieJar = response.cookies

    @task(1)
    def get_external_announce(self):
        with self.client.get("/moe/public/eFound/managMoe/externalAnnounce/",
                             catch_response=True,
                             cookies=self.cookieJar) as response:
            if response.status_code == 302:
                response.failure("Auth not pass!")
            elif response.status_code == 200:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    host = "http://140.124.39.132"
    wait_time = between(1.0, 5.0)
