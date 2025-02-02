from fastapi import FastAPI
from conexionBD import conexionBD
from pydantic import BaseModel

app = FastAPI()

db = conexionBD()

class mensajes_request(BaseModel):
    usuario : str
    carpeta : str

@app.get("/user/{usuario}")
def get_users(usuario: str):
    cursor = db.get_cursor()
    cursor.execute("SELECT nombre, apellido FROM usuario WHERE usuario = :usuario",{"usuario":usuario})
    user = cursor.fetchone()
    if user:
        return {
            "nombre": user[0],
            "apellido": user[1]
        }
    else:
        return {"mensaje": "Usuario no encontrado"}
    

@app.get("/carpetas")
def get_carpetas():
    cursor = db.get_cursor()
    cursor.execute("SELECT t.desctipocarpeta Nombre FROM tipocarpeta t")
    carpetas = [{"nombre":row[0]} for row in cursor.fetchall()]
    return carpetas

@app.get("/mensajes")
def get_mensajes(datos: mensajes_request):
    cursor = db.get_cursor()
    cursor.execute("SELECT ")    

