from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.cqlengine import connection

import settings


def setup_database_connection():
    try:
        auth_provider = PlainTextAuthProvider(
            username=settings.SCYLLA_DB_USER,
            password=settings.SCYLLA_DB_PASSWORD
        )
        cluster = Cluster(
            [settings.SCYLLA_DB_HOST],
            port=int(settings.SCYLLA_DB_PORT),
            auth_provider=auth_provider
        )
        session = cluster.connect()
        connection.set_session(session)
        connection.register_connection("cluster1", session=session, default=True)

    except Exception as e:
        print(f"An error occurred: {e}")
