from pathlib import Path
from locust import HttpUser, task
import asyncio
import msgpack
from holochain_client_user.user import HolochainUser
from holochain_client.api.admin.types import InstallApp, EnableApp
from holochain_client.api.app.types import ZomeCallUnsigned
from holochain_client.api.common.signing import authorize_signing_credentials
from locust import events
import random

class HelloWorldUser(HolochainUser):
    @task
    def hello_world(self):
        self.app_client.call_zome(
            ZomeCallUnsigned(
                cell_id=self.cell_id,
                zome_name="fixture",
                fn_name="create_fixture",
                payload=msgpack.packb({"name": "hello fixture"}),
            )
        )

    def on_start(self):
        # asyncio.set_event_loop(asyncio.new_event_loop())

        fixture_path = str((
            Path(__file__).parent / "../../fixture.happ"
        ).resolve())

        agent_pub_key = self.admin_client.generate_agent_pub_key()

        app_info = self.admin_client.install_app(
            InstallApp(
                agent_key=agent_pub_key,
                installed_app_id="test-app-" + str(random.randint(0, 1000)),
                path=fixture_path,
            )
        )

        self.admin_client.enable_app(EnableApp(app_info.installed_app_id))

        cell_id = app_info.cell_info["fixture"][0]["provisioned"]["cell_id"]
        self.event_loop.run_until_complete(
            authorize_signing_credentials(self.admin_client._admin_client, cell_id)
        )

        self.cell_id = cell_id
