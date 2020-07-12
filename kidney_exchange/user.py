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

#
# @login_manager.user_loader
# def user_loader(email):
#     if email not in users:
#         return
#
#     user = User()
#     user.id = email
#     return user
# 
#
# @login_manager.request_loader
# def request_loader(request):
#     email = request.form.get('email')
#     if email not in users:
#         return
#
#     user = User()
#     user.id = email
#
#     # DO NOT ever store passwords in plaintext and always compare password
#     # hashes using constant-time comparison!
#     user.is_authenticated = request.form['password'] == users[email]['password']
#
#     return user