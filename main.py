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

@app.get("/contactos/{usuario}")
def get_contactos(usuario: str):
    cursor = db.get_cursor()
    try:
        cursor.execute(f"SELECT c.conces, c.correocontacto FROM contacto c WHERE c.contactosUsuario = '{usuario}'")
        categorias = [{"id": row[0], "contacto": row[1]} for row in cursor.fetchall()]
        return categorias
    except Exception as e:
        return {"error": f"Error al obtener contactos: {e}"}
    finally:
        cursor.close() 



@app.get("/mensajes/{carpeta}/{usuario}")
def get_mensajes(carpeta: str, usuario: str):
    cursor = db.get_cursor()
    try:
        if carpeta == "Rec":
            query = f"""SELECT M.idmensaje id, M.men_usuario Remitente, C.correoContacto Destinatario, M.asunto Asunto,
                M.cuerpoMensaje Mensaje, to_char(M.fechaAccion, 'YYYY-MM-DD') Fecha
                FROM contacto C, mensaje M, destinatario D
                WHERE M.usuario = '{usuario}'
                AND M.idmensaje = D.idmensaje
                AND D.conces = C.conces
                AND M.idtipocarpeta = '{carpeta}'"""
            cursor.execute(query)
            mensajes = [{"id": row[0],"remitente": row[1], "destinatario" : row[2], "asunto": row[3], "mensaje": row[4], "fecha": row[5]} for row in cursor.fetchall()]
            return mensajes
        elif(carpeta in ["Env", "Bor"]):
            query = f"""SELECT M.idmensaje id, C.correoContacto Destinatario, D.idtipocopia Visibilidad, M.asunto Asunto,
                    M.cuerpoMensaje Mensaje, to_char(M.fechaAccion, 'YYYY-MM-DD') Fecha
                    FROM contacto C, mensaje M, destinatario D
                    WHERE M.usuario = '{usuario}'
                    AND M.idMensaje = D.idMensaje
                    AND D.conces = C.conces
                    AND M.idtipocarpeta = '{carpeta}'"""
            cursor.execute(query)
            mensajes = [{"id": row[0],"destinatario": row[1],"visibilidad":row[2], "asunto": row[3], "mensaje": row[4], "fecha": row[5]} for row in cursor.fetchall()]
            return mensajes

    except Exception as e:
        return {"error": f"Error al obtener mensajes: {e}"}
    finally:
        cursor.close()
  

