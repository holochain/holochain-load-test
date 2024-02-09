from locust import User

from holochain_client.api.app.client import AppClient
from holochain_client.api.admin.client import AdminClient
from holochain_client_user.admin_client_wrapper import AdminClientWrapper
from holochain_client_user.app_client_wrapper import AppClientWrapper
from urllib.parse import urlparse
import asyncio

class HolochainUser(User):

    abstract = True

    """A wrapped AdminClient which is instrumented to log requests with Locust."""
    admin_client: AdminClient

    """A wrapped AppClient which is instrumented to log requests with Locust."""
    app_client: AppClient

    def __init__(self, environment):
        super().__init__(environment)

        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        
        admin_client = AdminClient(self.host)
        admin_client.connect_sync(self.event_loop)
        self.admin_client = AdminClientWrapper(admin_client, self.event_loop, environment.events.request)
        
        app_ports = self.admin_client.list_app_interfaces()
        assert app_ports, "No app interfaces found"
        admin_url = urlparse(self.host)
        app_host = self.host.replace(str(admin_url.port), str(app_ports[0]))
        app_client = AppClient(app_host)
        app_client.connect_sync(self.event_loop)
        self.app_client = AppClientWrapper(app_client, self.event_loop, environment.events.request)
