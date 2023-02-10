# Load-testing with Locust.io
Locust is an open source load testing tool. Define user behaviour with Python code, and swarm your system with millions of simultaneous users.
visit [Locust.io](https://locust.io/)

## Installation
You may install inside the docker or your device
```shell
pip install locust
```

## How to run the load-testing
In the repository there have example of demo_manager app package APIs load testing.

***cards-server/loadtesting/demo_manager_api.py***

1. Install locust 
    
2. Run simple load-testing with UI
```shell
locust -f {test_file}

locust -f loadtesting/demo_manager_api.py
```
3. Now, we can access locust web ui with [ http://0.0.0.0:8089 ](http://0.0.0.0:8089)
There will have number of users, spawn rate, and host text input. filled all the number that you want to test


## More Details
Visit [Locust.io Documents](https://docs.locust.io/en/stable/index.html) for more details
