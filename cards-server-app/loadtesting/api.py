import json

from locust import HttpUser, task, TaskSet


class DemoManagerTestAppAPI(TaskSet):
    api_path = "/api/v1"
    auth_token = None

    def assert_request_success(self, response, label):
        if response.status_code != 200:
            response.failure(
                f"!!! {label} - Request failure with status code {response.status_code} e: {response.text}")
            return False

        response.success()
        return True

    def authorization_headers(self):
        return {
            "Authorization": f"Token {self.auth_token}"
        }

    def login(self):
        with self.client.request(
            method="POST",
            url=f"{self.api_path}/auth/login/",
            json={
                "email": "testuser@example.dev",
                "password": "Test1234567!"
            },
            catch_response=True
        ) as response:
            if self.assert_request_success(response, label="Login"):
                response_json = json.loads(response.text)
                self.auth_token = response_json["token"]

    def health_check(self):
        with self.client.request(method="GET", url="/ht", catch_response=True) as response:
            if response.elapsed.total_seconds() > 10:
                response.failure("!!! HealthCheck - Request took too long!")

            _ = self.assert_request_success(response, label="HealthCheck")

    def on_start(self):
        self.health_check()

    @task
    def get_books_with_index(self):
        self.login()

        with self.client.request(
            method="GET",
            url=f"{self.api_path}/demo/books_w_index/",
            headers=self.authorization_headers(),
            catch_response=True
        ) as books_response:
            request_duration_sec = books_response.elapsed.total_seconds()
            if self.assert_request_success(books_response, label="Get Books") and request_duration_sec > 40:
                books_response.failure(f"!!! Get Books - Request took too long! {request_duration_sec}")


class CardTestAppAPI(HttpUser):
    tasks = [DemoManagerTestAppAPI]
