from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from settings import SCYLLA_KEYSPACE


class BaseScyllaModel(Model):
    __abstract__ = True
    __keyspace__ = SCYLLA_KEYSPACE
    __connection__ = 'cluster1'


class Message(BaseScyllaModel):
    __table_name__ = 'message'
    topic_id = columns.UUID(primary_key=True, partition_key=True)
    created_at = columns.DateTime(primary_key=True, clustering_order="DESC")
    message_id = columns.UUID(primary_key=True)
    text = columns.Text()
    author_id = columns.UUID()
    is_edited = columns.Boolean()
    has_attachment = columns.Boolean()


class TopicsMember(BaseScyllaModel):
    __table_name__ = 'topics_member'
    topic_id = columns.UUID(primary_key=True, partition_key=True)
    user_id = columns.UUID(primary_key=True)
    role = columns.TinyInt()


class UsersTopic(BaseScyllaModel):
    __table_name__ = 'users_topic'
    user_id = columns.UUID(primary_key=True, partition_key=True)
    topic_id = columns.UUID(primary_key=True)
    role = columns.TinyInt()


class Topic(BaseScyllaModel):
    __table_name__ = 'topic'
    topic_id = columns.UUID(primary_key=True)
    title = columns.Text()
    topic_type = columns.TinyInt()


class Contact(BaseScyllaModel):
    __table_name__ = 'contact'
    user_id = columns.UUID(primary_key=True)
    contact_id = columns.UUID()
    nickname = columns.Text()
