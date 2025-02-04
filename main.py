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
    try:
        cursor.execute("SELECT nombre, apellido FROM usuario WHERE usuario = :usuario", {"usuario": usuario})
        user = cursor.fetchone()
        if user:
            return {"nombre": user[0], "apellido": user[1]}
        else:
            return {"mensaje": "Usuario no encontrado"}
    except Exception as e:
        return {"error": f"Error al obtener usuario: {e}"}
    finally:
        cursor.close()  # 🔹 Cierra el cursor después de la consulta
    

@app.get("/carpetas")
def get_carpetas():
    cursor = db.get_cursor()
    try:
        cursor.execute("SELECT t.idtipocarpeta, t.desctipocarpeta FROM tipocarpeta t")
        carpetas = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
        return carpetas
    except Exception as e:
        return {"error": f"Error al obtener carpetas: {e}"}
    finally:
        cursor.close()  # 🔹 Cierra el cursor después de la consulta


@app.get("/categorias")
def get_categorias():
    cursor = db.get_cursor()
    try:
        cursor.execute("SELECT c.idcategoria, c.desccategoria FROM categoria c")
        categorias = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
        return categorias
    except Exception as e:
        return {"error": f"Error al obtener categorías: {e}"}
    finally:
        cursor.close()  # 🔹 Cierra el cursor después de la consulta

@app.get("/mensajes/enviados/{usuario}")
def get_mensajes(usuario: str):
    cursor = db.get_cursor()
    try:
        query = """SELECT C.correoContacto Destinatario, M.asunto Asunto, 
                   M.cuerpoMensaje Mensaje, M.fechaAccion Fecha
                   FROM contacto C, mensaje M, destinatario D 
                   WHERE M.usuario = :usuario 
                   AND M.idMensaje = D.idMensaje 
                   AND D.conces = C.conces"""
        cursor.execute(query, {"usuario": usuario})
        mensajes = [{"destinatario": row[0], "asunto": row[1], "mensaje": row[2], "fecha": row[3]} for row in cursor.fetchall()]
        return mensajes
    except Exception as e:
        return {"error": f"Error al obtener mensajes: {e}"}
    finally:
        cursor.close()
  

