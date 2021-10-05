import socket
from _thread import *
import os
from datetime import datetime
import time
import pickle
import uuid

ip_jv = '192.168.100.8'


# guarda o diretorio onde o prog esta rodando
dir = os.path.dirname(os.path.realpath(__file__))
# abre diretorio
os.chdir(dir)
connections = [] 
# salva muma lista os nomes dos arquivos no diretorio
lista_arquivos = os.listdir()



def enviar_lista_arquivos(connection):
    data=pickle.dumps(lista_arquivos)
    connection.send(data)

def enviar_imagem(connection,nome_imagem):
    img = open(nome_imagem,'rb')
    data=pickle.dumps(img)
    connection.send(data)

def conexao_tcp_server(HOST='',PORT=5000):
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.settimeout(3.0)
    tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # dica da prof
    orig = (HOST, PORT)
    tcp.bind(orig)
    tcp.listen(1)
    con, cliente = tcp.accept()
    print ('Conectado com:', cliente)
    return con,cliente,tcp


class Servidor:
    port = 60000
    host = 'localhost'

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # dica da prof
        self.server_socket.bind(('', self.port))
        # para criar um ID unico de modo aleatorio
        self.id = str(uuid.uuid4()) 

    def espera_conexoes(self):
        while(True):
            mensagem, sourceAddress = self.server_socket.recvfrom(128)
            print("conectado com %s, mensagem: %s"%(sourceAddress, mensagem.decode("utf-8")))
            mensagem_decode = mensagem.decode("utf-8")

            # verifica o conteúdo das mensagens
            if 'pedir_arquivo' in mensagem_decode:
                nome_arquivo = mensagem_decode.replace('pedir_arquivo:','') # pega só o nome do arquivo
                print(nome_arquivo)
                if nome_arquivo in lista_arquivos:
                    try:
                        con,cliente,tcp = conexao_tcp_server()
                        enviar_imagem(con,nome_arquivo)
                        con.close()
                        tcp.close()                       
                    except socket.timeout:
                        print('Troca interrompida')
                        pass
                    except Exception as E:
                        print(f'Exception do Win: {E}')

            elif 'pedir_lista' == mensagem_decode:
                try:
                    con,cliente,tcp = conexao_tcp_server()
                    enviar_lista_arquivos(con)
                    con.close()
                    tcp.close()   
                    # time.sleep(0.5)
                    print(f'Meu id Server: {self.id}')
                    # envia seu ID
                    con2,cliente,tcp2 = conexao_tcp_server()
                    con2.send(str.encode(f'ID: {self.id}')) 
                    con2.close()
                    tcp2.close()                   
                except socket.timeout:
                    print('Troca interrompida')
                except Exception as E:
                    print(E)



    def listar_arquivos(self):
        return lista_arquivos

    def escreve_log(palavra, filename):
        f = open(filename, "a")
        f.write("{0} -- {1}\n".format(datetime.now().strftime("%d-%m-%Y %H:%M"), palavra))
        f.close()

    def local_ip():
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip


# funcao para mostrar a lista de arquivos recebida
def imprimir_lista(lista):
    cont = 0
    for i in lista:
        print(f'[{cont}]- {lista[i]}')
        cont += 1

def conexao_tcp_cliente(HOST='localhost',PORT=5000):
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.settimeout(3.0)
    tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    dest = (HOST, PORT)
    tcp.connect(dest)
    print('conect feita')
    return tcp


class Cliente:
    port = 60000
    host = '255.255.255.255' # para mandar broadcast
    cliente_socket = socket.socket()
    def __init__(self):
        self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cliente_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.cliente_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    def pedir_lista(self,mensagem):
        self.cliente_socket.sendto(str(mensagem).encode("utf-8"), (self.host, self.port))
        try: 
            tcp = conexao_tcp_cliente()
            msg = tcp.recv(1024)
            lista_recebida=pickle.loads(msg)
            # ordenar os nomes
            lista_recebida = sorted(lista_recebida)
            # time.sleep(0.5)
            
            print('Lista recebida do fulano:\n',lista_recebida)
            tcp.close()

            tcp2 = conexao_tcp_cliente()
            msg_id = tcp2.recv(1024)
            id = msg_id.decode('utf-8')
            id = id.replace('ID: ','')
            print(f'ID fulano: {msg_id}')
            tcp2.close()
        except socket.timeout:
            print('Nao foi possivel receber o arquivo solicitado')
        except Exception as E:
            print(E)



def main():
    # para print em azul
    CRED = '\33[36m'
    CEND = '\33[0m'
    comando = ''

    server = Servidor()
    start_new_thread(server.espera_conexoes,())

    cliente = Cliente()   

    while True:
        comando = input(f'{CRED}p2p>{CEND} ')
        if comando == 'conexoes':
            comando = ''
            print(connections)

        if 'pedir_arquivo' in comando:
            # server.espera_conexoes()
            cliente.pedir_arquivo(comando)
            comando = ''

        if comando == 'pedir_lista':
            cliente.pedir_lista(comando)
            comando = ''

        if comando == 'exit':
            exit(0)

        else:
            pass

 
        
if __name__ == '__main__':
   main()
