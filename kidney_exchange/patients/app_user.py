class AppUser:
    def __init__(
            self,
            id: int,
            email: str,
            pass_hash: str,
            role: str
    ):
        self._id = id,
        self._email = email
        self._pass_hash = pass_hash,
        self._role = role

    def __str__(self) -> str:
        return f"{{'id': '{self.id}', 'email': {str(self.email)}, , 'role': {str(self.role)}}}"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__ \
               and self.id == other.id

    @property
    def email(self) -> str:
        return self.email

    @property
    def id(self) -> int:
        return self.id

    @property
    def role(self) -> str:
        return self._role
