import cx_Oracle
from datetime import datetime
from typing import List
from fastapi import FastAPI
from conexionBD import conexionBD
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Definimos los permisos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = conexionBD()

#Modelo de los detinatarios
class destinatario(BaseModel):
    correo: str
    visibilidad: str

# Modelo de los mensajes
class mensaje(BaseModel):
    usuario: str
    asunto: str
    mensaje: str
    destinatarios: List[destinatario]
    archivos: List[str]

    
#Metodo para validar el usuario
@app.get("/user/{usuario}")
def get_users(usuario: str):
    cursor = db.get_cursor()
    try:
        #Consulta para validar si el usuario esta registrado
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
    
#Metodo para consultar las carpetas
@app.get("/carpetas")
def get_carpetas():
    cursor = db.get_cursor()
    try:
        # Consultamos todas las carpetas
        cursor.execute("SELECT t.idtipocarpeta, t.desctipocarpeta FROM tipocarpeta t")
        carpetas = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
        return carpetas
    except Exception as e:
        return {"error": f"Error al obtener carpetas: {e}"}
    finally:
        cursor.close()

# Metodo para consultar categorias
@app.get("/categorias")
def get_categorias():
    cursor = db.get_cursor()
    try:
        # Consultamos todas las categorias
        cursor.execute("SELECT c.idcategoria, c.desccategoria FROM categoria c")
        categorias = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
        return categorias
    except Exception as e:
        return {"error": f"Error al obtener categorías: {e}"}
    finally:
        cursor.close()

# Metodo para consultar los contactos de un usuario
@app.get("/contactos/{usuario}")
def get_contactos(usuario: str):
    cursor = db.get_cursor()
    try:
        # Consultamos los contactos del usuario
        cursor.execute(f"""SELECT c.conces, NVL(c.usuariocontacto, c.correocontacto) 
                FROM contacto c 
                WHERE c.contactosUsuario = '{usuario}'""")
        categorias = [{"id":row[0], "contacto": row[1]} for row in cursor.fetchall()]
        return categorias
    except Exception as e:
        return {"error": f"Error al obtener contactos: {e}"}
    finally:
        cursor.close() 

# Metodo para consultar los tipos de archivo
@app.get("/tipoArchivos")
def get_tipoArchivos():
    cursor = db.get_cursor()
    try:
        # Consultamos los tipos de archivo
        cursor.execute(f"""SELECT idtipoarchivo FROM tipoarchivo""")
        categorias = [{"tipo":row[0]} for row in cursor.fetchall()]
        return categorias
    except Exception as e:
        return {"error": f"Error al obtener tipo Archivos: {e}"}
    finally:
        cursor.close() 

# Metodo para consultar los mensajes segun la carpeta y el usuario
@app.get("/mensajes/{carpeta}/{usuario}")
def get_mensajes(carpeta: str, usuario: str):
    cursor = db.get_cursor()
    try:
        # Validamos si la carpeta es recibidos
        if carpeta == "Rec":
            # Consultamos los mensajes que tiene en recibidos el usuario
            query = f"""SELECT M.idmensaje id, M.men_usuario Remitente, M.asunto Asunto,
                M.cuerpoMensaje Mensaje, to_char(M.fechaAccion, 'YYYY-MM-DD') Fecha
                FROM mensaje M
                WHERE M.usuario = '{usuario}'
                AND M.idtipocarpeta = '{carpeta}'"""
            cursor.execute(query)
            mensajes = [{"id": row[0],"remitente": row[1], "asunto": row[2], "mensaje": row[3], "fecha": row[4]} for row in cursor.fetchall()]
            for mensaje in mensajes:
                # Consultamos los destinatarios de cada mensaje
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
                # Consultamos los archivos adjuntos de cada mensaje
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
        # Caso en que se consulte enviados o borradores
        elif(carpeta in ["Env", "Bor"]):
            # Consultamos los mensajes que estan en enviados o borradores
            query = f"""SELECT M.idmensaje id, M.asunto Asunto,
                    M.cuerpoMensaje Mensaje, to_char(M.fechaAccion, 'YYYY-MM-DD') Fecha
                    FROM mensaje M
                    WHERE M.usuario = '{usuario}'
                    AND M.idtipocarpeta = '{carpeta}'"""
            cursor.execute(query)
            mensajes = [{"id": row[0], "asunto": row[1], "mensaje": row[2], "fecha": row[3]} for row in cursor.fetchall()]
            for mensaje in mensajes:
                # Consultamos los destinatarios de cada mensaje
                query = f"""SELECT C.correocontacto, D.idtipocopia 
                    FROM destinatario D
                    JOIN contacto C ON C.conces = D.conces
                    WHERE 
                        D.usuario = '{usuario}'
                        AND D.idmensaje = '{mensaje["id"]}'"""
                cursor.execute(query)
                destinatarios = [{"destinatario":row[0], "visibilidad":row[1]} for row in cursor.fetchall()]
                mensaje["destinatarios"] = destinatarios
                # Consultamos los archivos de cada mensaje
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
        else:
            # Consultamos los mensajes segun categorias
            query = f"""SELECT M.idmensaje id, M.men_usuario Remitente, M.asunto Asunto,
                M.cuerpoMensaje Mensaje, to_char(M.fechaAccion, 'YYYY-MM-DD') Fecha
                FROM mensaje M
                WHERE M.usuario = '{usuario}'
                AND M.idtipocarpeta = 'Rec'
                AND M.idcategoria = '{carpeta}'"""
            cursor.execute(query)
            mensajes = [{"id": row[0],"remitente": row[1], "asunto": row[2], "mensaje": row[3], "fecha": row[4]} for row in cursor.fetchall()]
            for mensaje in mensajes:
                # Consultamos los destinatarios de cada mensaje
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
                # Consultamos los archivos adjuntos de cada mensaje
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
    except Exception as e:
        return {"error": f"Error al obtener mensajes: {e}"}
    finally:
        cursor.close()
  
# Metodo para crear un mensaje
@app.post("/enviar")
def post_mesnaje(datos: mensaje):
    cursor = db.get_cursor()
    try:
        #Consultamos el siguiente consecutivo
        cursor.execute("SELECT MAX(TO_NUMBER(idmensaje)) FROM mensaje")
        idmensaje = int(cursor.fetchone()[0]) + 1
        fecha_actual = datetime.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now().strftime('%H:%M:%S')
        # Insertamos el mensaje creado por el usuario
        query = f"""INSERT INTO mensaje (USUARIO, IDMENSAJE, IDCATEGORIA, IDPAIS, MEN_USUARIO, 
                MEN_IDMENSAJE, IDTIPOCARPETA, ASUNTO, CUERPOMENSAJE, FECHAACCION, HORAACCION)
                VALUES ('{datos.usuario}', '{idmensaje}', 'PRI', '169', null, null, 'Env', '{datos.asunto}',
                '{datos.mensaje}', to_date('{fecha_actual}', 'YYYY-MM-DD'), to_date('{hora_actual}', 'HH24:MI:SS'))
        """
        cursor.execute(query)
        # Insertamos los archivos 
        for archivo in datos.archivos:
            cursor.execute("SELECT MAX(consecArchivo) from archivoadjunto")
            consecArchivo = int(cursor.fetchone()[0])+1
            query = f"""INSERT INTO archivoadjunto (CONSECARCHIVO, IDTIPOARCHIVO, USUARIO, IDMENSAJE, NOMARCHIVO)
                    VALUES ({consecArchivo}, '{archivo[-3:].upper()}', '{datos.usuario}', '{idmensaje}', '{archivo}')
                    """
            cursor.execute(query)
        # Insercion de destinatarios
        for destinatario in datos.destinatarios:

            #Validamos si el destinatario es un usuario registrado
            if '@' in destinatario.correo:
                # Validamos si existe el contacto
                query = f"""SELECT conces from contacto 
                WHERE contactosusuario = '{datos.usuario}' AND correocontacto = '{destinatario.correo}'
                """
                cursor.execute(query)
                conces = [{"conces":row[0]} for row in cursor.fetchall()][0]["conces"]
                # En caso de que no creamos el contacto
                if not conces:
                    cursor.execute("SELECT MAX(conces) from contacto")
                    conces = int(cursor.fetchone()[0])+1
                    query = f"""INSERT INTO contacto (conces, usuariocontacto, contactosusuario, nombrecontacto, correocontacto)
                        VALUES ({conces}, NULL, '{datos.usuario}', NULL, '{destinatario.correo}')
                        """
                    cursor.execute(query)
            else:
                # Validamos que exista el usuario en la base
                query = f"""SELECT nombre from usuario 
                WHERE usuario = '{destinatario.correo}'
                """
                cursor.execute(query)
                nombre = cursor.fetchone()[0]
                # Validamos que exista el contacto
                if nombre:
                    query = f"""SELECT conces from contacto 
                    WHERE usuarioContacto = '{destinatario.correo}' AND contactosUsuario = '{datos.usuario}'
                    """
                    cursor.execute(query)
                    conces = [{"conces":row[0]} for row in cursor.fetchall()][0]["conces"]
                    # Si no exite lo creamos
                    if not conces:
                        cursor.execute("SELECT MAX(conces) from contacto")
                        conces = int(cursor.fetchone()[0])+1
                        query= f"""INSERT INTO contacto (conces, usuariocontacto, contactosusuario, nombrecontacto, correocontacto)
                        VALUES ({conces}, '{destinatario.correo}', '{datos.usuario}', '{nombre}', '{destinatario.correo+'@BD.edu.co'}')
                        """
                        cursor.execute(query)
                    # Insertamos el mensaje para el destinatario
                    query = f"""INSERT INTO mensaje (USUARIO, IDMENSAJE, IDCATEGORIA, IDPAIS, MEN_USUARIO, MEN_IDMENSAJE, 
                                IDTIPOCARPETA, ASUNTO, CUERPOMENSAJE, FECHAACCION, HORAACCION) 
                            VALUES ('{destinatario.correo}', '{idmensaje}', 'PRI','169','{datos.usuario}',
                            '{idmensaje}', 'Rec', '{datos.asunto}','{datos.mensaje}',
                            to_date('{fecha_actual}','YYYY-MM-DD'),to_date('{hora_actual}','HH24:MI:SS'))"""
                    cursor.execute(query)
                    
                else:
                    break
            # Insertamos los destinatarios
            cursor.execute("SELECT MAX(consecDestinatario) from destinatario")
            consecDestinatario = int(cursor.fetchone()[0])+1
            query = f"""INSERT INTO destinatario (CONSECDESTINATARIO, CONCES, IDTIPOCOPIA, USUARIO, IDMENSAJE, IDPAIS)
                VALUES ({consecDestinatario}, {conces}, '{destinatario.visibilidad}', '{datos.usuario}', '{idmensaje}', '169')
                """
            cursor.execute(query)
        
        db.commit()
        return {"message": "Se ha enviado el mensaje"}
    except cx_Oracle.DatabaseError as e:
        db.rollback()
        return {"message": "Error al enviar mensajes"}
    finally:
        cursor.close()
