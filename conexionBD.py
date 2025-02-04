import cx_Oracle

class conexionBD:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(conexionBD, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            USER = "BD8224"
            PASSWORD = "BD8224"
            HOST = "localhost"
            PORT = "1521"
            SID = "XE"

            dsn = cx_Oracle.makedsn(HOST, PORT, service_name=SID)
            self.connection = cx_Oracle.connect(USER, PASSWORD, dsn)
            print("✅ Conexión exitosa a Oracle")
        except cx_Oracle.DatabaseError as e:
            print(f"❌ Error de conexión: {e}")

    def get_cursor(self):
        return self.connection.cursor()  # Devuelve un cursor nuevo en cada llamada

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()
        print("🔌 Conexión cerrada")
