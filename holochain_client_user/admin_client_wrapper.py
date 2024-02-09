import time
from holochain_client.api.admin.client import AdminClient
import asyncio

class AdminClientWrapper:
    def __init__(self, admin_client: AdminClient, event_loop, request_event):
        self._admin_client = admin_client
        self._event_loop = event_loop
        self._request_event = request_event
    
    def __getattr__(self, name):
        func = getattr(self._admin_client, name)
        
        def wrapper(*args, **kwargs):
            request_meta = {
                "request_type": "hc-admin-ws",
                "name": name,
                "start_time": time.time(),
                "response_length": 0,  # TODO No way to get this from the client at the moment
                "response": None,
                "context": {},  # see HttpUser if you actually want to implement contexts
                "exception": None,
            }
            start_perf_counter = time.perf_counter()
            try:
                request_meta["response"] = self._event_loop.run_until_complete(func(*args, **kwargs))
            except Exception as e:
                request_meta["exception"] = e
            request_meta["response_time"] = (time.perf_counter() - start_perf_counter) * 1000
            self._request_event.fire(**request_meta)  # Log the request with Locust

            if request_meta["exception"]:
                raise request_meta["exception"]

            return request_meta["response"]

        return wrapper
