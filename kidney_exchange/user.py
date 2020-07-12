import flask_login


class User(flask_login.UserMixin):
    def __init__(
            self,
            email
    ):
        self.id = email

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self._authenticated

    def set_authenticated(self, authenticated: bool):
        self._authenticated = authenticated

    def is_anonymous(self):
        return False
