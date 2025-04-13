from .entities.User import User
from werkzeug.security import generate_password_hash

class ModelUser():

    @classmethod
    def login(self,db,user):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id, Usuario, Contraseña, Nombre, Apellido FROM usuarios 
                    WHERE Usuario = '{}'""".format(user.username)
            cursor.execute(sql)
            row=cursor.fetchone()

            if row != None:
                user = User(row[0], row[1], User.check_password(row[2], user.password), row[3], row[4])
                return user
            
            else:
                return None

        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def registrar(cls, db, user):
        try:
            cursor = db.connection.cursor()

            sql_insert = """INSERT INTO usuarios (Usuario, Contraseña, Nombre, Apellido)
                            VALUES (%s, %s, %s, %s);"""
            cursor.execute(sql_insert, (user.username, generate_password_hash(user.password), user.nombre, user.apellido))
            db.connection.commit()

            sql_select = """SELECT id, Usuario, Contraseña, Nombre, Apellido 
                            FROM usuarios WHERE Usuario = %s;"""
            cursor.execute(sql_select, (user.username,))
            row = cursor.fetchone()

            if row is not None:
                return User(row[0], row[1], User.check_password(row[2], user.password), row[3], row[4])
            else:
                return None

        except Exception as ex:
            raise Exception(ex)
    
    @classmethod
    def get_by_id(self,db,id):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id, Usuario, Nombre, Apellido FROM usuarios 
                    WHERE id = '{}'""".format(id)
            cursor.execute(sql)
            row=cursor.fetchone()

            if row != None:
                return User(row[0], row[1], None, row[2], row[3])
            
            else:
                return None

        except Exception as ex:
            raise Exception(ex)