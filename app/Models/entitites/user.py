from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class User(UserMixin):
    
    def get_id(self):
        return (self.id_usuario)

    def __init__(self, id_usuario, username, password, rol, activo):
        self.id_usuario = id_usuario
        self.username = username
        self.password = password
        self.rol = rol
        self.activo = activo

    @classmethod
    def check_password(cls, hashed_password, password):
        return check_password_hash(hashed_password, password)
 