import socket
from _thread import *
import os
from datetime import datetime
import time
import pickle
import uuid
import random
from timeit import default_timer as timer
import sys

ip_jv = '192.168.100.8'


# guarda o diretorio onde o prog esta rodando
dir = os.path.dirname(os.path.realpath(__file__))
# abre diretorio
os.chdir(dir)
connections = [] 
# salva muma lista os nomes dos arquivos no diretorio
lista_arquivos = os.listdir()
id = str(random.randint(1,1000))


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
    # print ('Conectado com:', cliente)
    return con,cliente,tcp

def escreve_log(palavra, filename):
        f = open(filename, "a")
        f.write("{0} -- {1}\n".format(datetime.now().strftime("%d-%m-%Y %H:%M"), palavra))
        f.close()

class Servidor:
    port = 60000
    host = 'localhost'

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # dica da prof
        self.server_socket.bind(('', self.port))
        # para criar um ID unico de modo aleatorio
         

    def espera_conexoes(self):
        while(True):
            mensagem, sourceAddress = self.server_socket.recvfrom(128)
            print("conectado com %s, mensagem: %s"%(sourceAddress, mensagem.decode("utf-8")))
            mensagem_decode = mensagem.decode("utf-8")


            if 'procurar_arquivo' in mensagem_decode:
                nome_arquivo = mensagem_decode.replace('procurar_arquivo:','') # pega só o nome do arquivo
                print(nome_arquivo)
                if nome_arquivo in lista_arquivos:
                    try:
                        con,cliente,tcp = conexao_tcp_server()
                        con.send(str.encode(id))
                        con.close()
                        tcp.close()                       
                    except socket.timeout:
                        print('Troca interrompida')
                        pass
                    except Exception as E:
                        print(f'Exception do Win: {E}')

            elif 'lista arquivos' in mensagem_decode:
                # pegar o ID e verificar se e ID solicitado
                num_id = mensagem_decode.replace('lista arquivosID:','') # pega só ID
                # print(f'pedido para ID: {type(num_id)}')
                if num_id == id:
                    try:
                        con,cliente,tcp = conexao_tcp_server()
                        enviar_lista_arquivos(con)
                        con.close()
                        tcp.close()   
                        time.sleep(0.3)
    
                        # envia seu ID
                        con2,cliente,tcp2 = conexao_tcp_server()
                        con2.send(str.encode(f'ID: {str(id)}')) 
                        con2.close()
                        tcp2.close()                   
                    except socket.timeout:
                        print('Troca interrompida')
                    except Exception as E:
                        print(f'Exception do Win: {E}')

            elif 'pedir_IDs' == mensagem_decode:
                try:
                    con,cliente,tcp = conexao_tcp_server()
                    con.send(str.encode(id))
                    con.close()
                    tcp.close()   
                 
                except socket.timeout:
                    print('Troca interrompida')
                except Exception as E:
                    print(f'Exception do Win: {E}')


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
    # print('conect feita')
    return tcp


class Cliente:
    port = 60000
    host = '255.255.255.255' # para mandar broadcast
    cliente_socket = socket.socket()
    def __init__(self):
        self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cliente_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.cliente_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def pedir_usuarios(self):
        self.cliente_socket.sendto(str('pedir_IDs').encode("utf-8"), (self.host, self.port))
        try: 
            while True:
                try:
                    tcp = conexao_tcp_cliente()
                    tcp.settimeout(1.0)
                    msg = tcp.recv(1024)
                    tcp.close()
                    msg_decode = msg.decode('utf-8')
                    # para nao salvar IDs repetidos
                    if not msg_decode in connections:
                        connections.append(msg_decode)

                except socket.timeout:
                    break

        except socket.timeout:
            pass
        except Exception as E:
            # print(f'Exception do Win: {E}')
            pass

    def pedir_listas_arquivos(self,mensagem,lista_ids=connections):
        # Solicita via BROADCAST a lista arquivos de cada usuário na rede
        # self.cliente_socket.sendto(str(mensagem).encode("utf-8"), (self.host, self.port))

        # para atualizar a lista de usuarios
        self.pedir_usuarios()
        try: 
            for id in connections:
                try:
                    # pedido de arquivo com o ID de um servidor
                    self.cliente_socket.sendto(str(mensagem + f'ID:{id}').encode("utf-8"), (self.host, self.port))
                    tcp = conexao_tcp_cliente()
                    tcp.settimeout(1.0)
                    msg = tcp.recv(1024)
                    lista_recebida=pickle.loads(msg)
                    # ordenar os nomes
                    lista_recebida = sorted(lista_recebida)
                    # time.sleep(0.5)
                    
                    tcp.close()
                    time.sleep(0.3)
                    tcp2 = conexao_tcp_cliente()
                    msg_id = tcp2.recv(1024)
                    id_rcv = msg_id.decode('utf-8')
                    id_rcv = id_rcv.replace('ID: ','')
                    print(f'Lista: {lista_recebida} recebida do prog de ID: {id_rcv}\n')
                    tcp2.close()
                except socket.timeout:
                    break
        except socket.timeout:
            print('Nao foi possivel receber o arquivo solicitado')
        except Exception as E:
            # print(f'Exception do Win (pedir_listas_arquivos): {E}')
            pass



    def procurar_arquivo(self,comando):
        # Enviar broadcast com o nome de um arquivo, retornar os IDs de quem possui
        nodes_com_arq = []
        self.cliente_socket.sendto(str(comando).encode("utf-8"), (self.host, self.port))

        while True:
            try:
                tcp = conexao_tcp_cliente()
                tcp.settimeout(1.0)
                msg = tcp.recv(1024)
                tcp.close()
                msg_decode = msg.decode('utf-8')
                nodes_com_arq.append(msg_decode)

            except:
                break
        
        print(f'Nodes com o arquivo solicitado:{nodes_com_arq}')


    def baixar_arquivo(self,comando):
        #Criar uma conexão TCP com um node através do seu ID e baixar o arquivo requisitado
        pass

def print_menu():
    CBLUE = '\33[104m'
    CEND = '\33[0m'
    print('-*'* 10 + f' {CBLUE}COMANDOS{CEND} '+ '-*'* 10)
    print('Lista de pares conectados: conexoes')
    print('Procurar arquivo:          procurar_arquivo:nome.formato')
    print('Baixar arquivo:            baixar_arquivo:nome.formato-ID')
    print('Pedir listas de arquivos:  lista arquivos')
    print('Listar nodes da rede:      usuarios')
    print('Fechar programa:           exit')
    print('limpar terminal:           clear')

def main():
    # para print em azul
    CRED = '\33[36m'
    CEND = '\33[0m'
    comando = ''

    server = Servidor()
    start_new_thread(server.espera_conexoes,())

    cliente = Cliente()   

    print(f'ID node: {id}\n')
    print(f'Meus arquivos: {lista_arquivos}\n')
    #print_menu()

    while True:
        comando = input(f'{CRED}p2p>{CEND} ')

        if 'comandos' in comando:
            print_menu()

        if comando == 'conexoes':
            comando = ''
            print(f'Lista de Nodes na rede: {connections}')

        # ex: procurar_arquivo:vasco.jpg
        if 'procurar_arquivo' in comando:
            nome_arquivo_proc = comando.replace('procurar_arquivo:','')
            if nome_arquivo_proc in lista_arquivos:
                print(f'Você já possui o arquivo {nome_arquivo_proc}')
            cliente.procurar_arquivo(comando)
            comando = ''
        
        # ex: baixar_arquivo:vasco.jpg-ID
        if 'baixar_arquivo' in comando:
            cliente.baixar_arquivo(comando)
            comando = ''
        # para pedir lista de arquivos de todos os servidores ativos
        if comando == 'lista arquivos':
            cliente.pedir_listas_arquivos(comando)
            comando = ''

        if comando == 'usuarios':
            cliente.pedir_usuarios()
            print(f'Lista de Nodes na rede: {connections}')
            comando = ''

        if comando == 'exit':
            sys.exit()

        if comando == 'clear':
            print("\x1b[2J\x1b[1;1H")
        else:
            pass

 
        
if __name__ == '__main__':
   main()
