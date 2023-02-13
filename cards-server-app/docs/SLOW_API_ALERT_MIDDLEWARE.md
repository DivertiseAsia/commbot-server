# Slow API Alert Middleware
This Middleware will send a `signal` when API took time to response more than expected.

## Set Up
1. Add middleware into `MIDDLEWARE` config in `settings.py`.

    ***NOTE:*** put the `SlowAPIAlertMiddleware` above the `CommonMiddleware`

```python
MIDDLEWARE = [
    ...,
    "config.middleware.slow_api.SlowAPIAlertMiddleware",
    "django.middleware.common.CommonMiddleware",
]
```
2. Create a `signal` to handling the alert.

```python
# demo_manager/signals.py
from django.dispatch import receiver

from config.middleware.slow_api import slow_api_alert_triggered

@receiver(slow_api_alert_triggered)
def handle_slow_api_alert_triggered(sender, alert_data, *args, **kwargs):
    print("handle logic")
```

3. Setup a `signal` for ready use
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
