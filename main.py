from fastapi import FastAPI
from conexionBD import conexionBD
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes cambiar "*" por una lista de dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

db = conexionBD()

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
    cursor.execute("SELECT t.idtipocarpeta, t.desctipocarpeta FROM tipocarpeta t")
    carpetas = [{"id": row[0], "nombre":row[1]} for row in cursor.fetchall()]
    return carpetas

@app.get("/categorias")
def get_categorias():
    cursor = db.get_cursor()
    cursor.execute("SELECT c.idcategoria, c.desccategoria  FROM categoria c")
    categorias = [{"id": row[0], "nombre":row[1]} for row in cursor.fetchall()]
    return categorias

@app.get("/mensajes/enviados/{usuario}")
def get_mensajes(usuario: str):
    cursor = db.get_cursor()
    query = """SELECT C.correoContacto Destinatario, M.asunto Asunto, M.cuerpoMensaje Mensaje, M.fechaAccion Fecha
    from contacto C, mensaje M, destinatario D WHERE M.usuario = '""" + usuario +"""' and
     M.idMensaje = D.idMensaje and D.conces = C.conces"""
    cursor.execute(query)
    mensajes = []    

