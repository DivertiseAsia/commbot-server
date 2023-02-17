# Middleware Failed API Alert 
This Middleware will send a `signal` when API has failed response.

## Set Up
1. Add middleware into `MIDDLEWARE` config in `settings.py`.

    ***NOTE:*** put the `FailedAPIAlertMiddleware` bottom of other request middles

```python
MIDDLEWARE = [
    ...,
    "config.middleware.failed_api.FailedAPIAlertMiddleware"
]
```
2. Set configs.
```python
# config/settings.py
FAILED_API_ALERT_NAMESPACES = ["demo", "v1", "rest_framework", "social", "password_reset"] # required
FAILED_API_ALERT_STATUS_CODES = [400] # required
```
3. Create a `signal` to handling the alert.
```python
# demo_manager/signals.py
from django.dispatch import receiver

from config.middleware.failed_api import failed_api_alert_triggered

@receiver(failed_api_alert_triggered)
def handle_failed_api_alert_triggered(sender, request, request_body, response, alert_data, *args, **kwargs):
    print("handle logic")
```
4. Setup a `signal` for ready use.
   1. Add `ready` function in `AppConfig`
       ```python
       # demo_manager/apps.py
    
       def ready(self):
           import demo_manager.signals
       ```
   2. Add `default_app_config` in `init.py`
      ```python 
      # demo_manager/__init__.py
      default_app_config = "demo_manager.apps.DemoManagerConfig"
      ```
