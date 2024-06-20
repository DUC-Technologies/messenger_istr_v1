from messenger.db import AbstractContactDAL
from messenger.schemas import ContactCreate, UserID, ContactUpdate, ContactDelete


class ContactService:
    def __init__(self, dal: AbstractContactDAL):
        self.dal = dal

    def create_contact(self, body: ContactCreate):
        return self.dal.create_contact(body.user_id, body.contact_id, body.nickname)

    def get_contacts(self, body: UserID):
        return self.dal.get_contacts_by_user_id(body.user_id)

    def update_contact(self, body: ContactUpdate):
        return self.dal.update_contact(body.user_id, body.contact_id, body.contact_id)

    def delete_contact(self, body: ContactDelete):
        self.dal.delete_contact(body.user_id, body.contact_id)
