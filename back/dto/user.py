from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import dataclass_json

import back.models as models


@dataclass_json
@dataclass
class User:
    '''
    Data structure for user information.
    '''
    user_id: int
    social_id: str
    name: str
    email: str
    avatar: str
    creation_date: datetime
    is_admin: bool
    is_active: bool

    def to_model(self):
        '''
        Returns a User model object
        based on the invoking User DTO object
        '''
        user_model=models.Users(id=self.user_id, social_id=self.social_id, name=self.name, email=self.email, avatar=self.avatar, creation_date=self.creation_date, is_admin=self.is_admin, is_active=self.is_active)
        return user_model
