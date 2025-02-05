from fastapi import FastAPI
from conexionBD import conexionBD
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        cursor.close()
    

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
        cursor.close()


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
        cursor.close()

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
            query = f"""SELECT DISTINCT M.idmensaje id, M.men_usuario Remitente, M.asunto Asunto,
                M.cuerpoMensaje Mensaje, to_char(M.fechaAccion, 'YYYY-MM-DD') Fecha
                FROM mensaje M
                WHERE M.usuario = '{usuario}'
                AND M.idtipocarpeta = '{carpeta}'"""
            cursor.execute(query)
            mensajes = [{"id": row[0],"remitente": row[1], "asunto": row[2], "mensaje": row[3], "fecha": row[4]} for row in cursor.fetchall()]
            for mensaje in mensajes:
                query = f"""SELECT C.correocontacto, D.idtipocopia 
                    FROM destinatario D
                    JOIN contacto C ON C.conces = D.conces
                    WHERE 
                        ((D.idtipocopia = 'CO') 
                        OR 
                        (D.idtipocopia = 'COO' AND C.usuarioContacto = '{usuario}'))
                        AND D.usuario = '{mensaje["remitente"]}'
                        AND D.idmensaje = '{mensaje["id"]}'"""
                cursor.execute(query)
                destinatarios = [{"destinatario":row[0], "visibilidad":row[1]} for row in cursor.fetchall()]
                mensaje["destinatarios"] = destinatarios
                query = f"""SELECT A.nomarchivo
                    FROM archivoadjunto A, mensaje M
                    WHERE A.usuario = M.men_usuario
                    AND A.idmensaje = M.men_idmensaje
                    AND M.men_idmensaje = '{mensaje["id"]}'
                    AND M.usuario = '{usuario}'"""
                cursor.execute(query)
                archivos = [{"nombre":row[0]} for row in cursor.fetchall()]
                mensaje["archivos"] = archivos
            return mensajes
        elif(carpeta in ["Env", "Bor"]):
            query = f"""SELECT M.idmensaje id, M.asunto Asunto,
                    M.cuerpoMensaje Mensaje, to_char(M.fechaAccion, 'YYYY-MM-DD') Fecha
                    FROM mensaje M
                    WHERE M.usuario = '{usuario}'
                    AND M.idtipocarpeta = '{carpeta}'"""
            cursor.execute(query)
            mensajes = [{"id": row[0], "asunto": row[1], "mensaje": row[2], "fecha": row[3]} for row in cursor.fetchall()]
            for mensaje in mensajes:
                query = f"""SELECT C.correocontacto, D.idtipocopia 
                    FROM destinatario D
                    JOIN contacto C ON C.conces = D.conces
                    WHERE 
                        (D.idtipocopia = 'CO') 
                        AND D.usuario = '{usuario}'
                        AND D.idmensaje = '{mensaje["id"]}'"""
                cursor.execute(query)
                destinatarios = [{"destinatario":row[0], "visibilidad":row[1]} for row in cursor.fetchall()]
                mensaje["destinatarios"] = destinatarios
            return mensajes

    except Exception as e:
        return {"error": f"Error al obtener mensajes: {e}"}
    finally:
        cursor.close()
  

