from .entitites.user import User

class ModelUser():
    @classmethod
    def login(self, db, user):
        try:
            cur=db.cursor()
            sql="SELECT id_usuario, name, password FROM usuarios WHERE activo='true' and name='{}'".format(user.username)
            cur.execute(sql,)
            row=cur.fetchone()
            if row != None:
                user=User(row[0], row[1], user.check_password(row[2],user.password), None, None)
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def get_by_id(self, db, id_usuario):
        try:
            cur=db.cursor()
            sql="SELECT id_usuario, name, password, rol, activo FROM usuarios WHERE usuarios.activo='true' and id_usuario='{}'".format(id_usuario)
            cur.execute(sql)
            row=cur.fetchone()
            if row != None:
                return User (row[0], row[1], None, row[2], row[3])
            else:
                return None 
        except Exception as ex:
            raise Exception (ex)