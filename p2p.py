import socket
from _thread import *
import os
from datetime import datetime
import time
import pickle
import uuid
import random
from timeit import default_timer as timer

ip_jv = '192.168.100.8'
connections = []
id = str(random.randint(1,1000))

# funcao para retornar tamanho de um arquivo em Bytes
def getSize(filename):
    st = os.stat(filename)
    return st.st_size

def meus_arquivos():
    # guarda o diretorio onde o prog esta rodando
    dir = os.path.dirname(os.path.realpath(__file__))
    # abre diretorio
    os.chdir(dir)
     
    # salva muma lista os nomes dos arquivos no diretorio
    return os.listdir()

# funcao para enviar arquivo
def enviar_arquivo(connection,nome):
    file = open(nome,'rb')
    data=pickle.dumps(file)
    connection.send(data)

def enviar_lista_arquivos(connection):
    data=pickle.dumps(meus_arquivos())
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


            if 'procurar arquivo' in mensagem_decode:
                nome_arquivo = mensagem_decode.replace('procurar arquivo:','') # pega só o nome do arquivo

                lista_arquivos = meus_arquivos()
                if nome_arquivo in lista_arquivos:
                    try:
                        # abre o arquivo para descobrir seu tamanho e enviar junto com o id
                        file = open(nome_arquivo,'rb')
                        tamanho_file = f', {getSize(nome_arquivo)} Bytes'
                        file.close()
                        con,cliente,tcp = conexao_tcp_server()
                        con.send(str.encode('ID: '+ id + tamanho_file))
                        con.close()
                        tcp.close()                       
                    except socket.timeout:
                        print('Troca interrompida')
                        pass
                    except Exception as E:
                        print(f'Exception do Win (espera_conexoes): {E}')

            elif 'lista arquivos' in mensagem_decode:
                # pegar o ID e verificar se e ID solicitado
                num_id = mensagem_decode.replace('lista arquivosID:','') # pega só ID

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
                        print(f'Exception do Win (espera_conexoes): {E}')

            elif 'pedir_IDs' == mensagem_decode:
                try:
                    con,cliente,tcp = conexao_tcp_server()
                    con.send(str.encode(id))
                    con.close()
                    tcp.close()   
                 
                except socket.timeout:
                    print('Troca interrompida')
                except Exception as E:
                    print(f'Exception do Win (espera_conexoes): {E}')

            elif 'baixar arquivo' in mensagem_decode:
                mensagem_decode = mensagem_decode.replace('baixar arquivo:','') # pega só nome do arquivo e ID
                num_id = mensagem_decode[mensagem_decode.find('-')+1:]
                nome_arquivo = mensagem_decode[:mensagem_decode.find('-')]

                if num_id == id:
                    con,cliente,tcp = conexao_tcp_server()

                    file = open(nome_arquivo,'rb')
                    con.sendfile(file, offset=0, count=None)
                    print(f'Enviados {file.tell()} Bytes')
                    con.close()
                    tcp.close() 
                    file.close()

                    print('Envio de arquivo concluído\n')




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
            # print(f'Exception do Win (pedir_usuarios): {E}')
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
                    print(f'Lista: {lista_recebida} recebida do Node de ID: {id_rcv}\n')
                    tcp2.close()
                except socket.timeout:
                    break
        except socket.timeout:
            print('Nao foi possivel receber o arquivo solicitado')
        except Exception as E:
            # print(f'Exception do Win (pedir_listas_arquivos): {E}')
            pass



    def procurar_arquivo(self,comando):
        CYELLOW = '\33[93m'
        CEND = '\33[0m'
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
        
        print(f'{CYELLOW}Nodes com o arquivo solicitado{CEND}:{nodes_com_arq}')

    # funcao que solicita um arquivo para o servidor
    def solicita_arquivo(self,comando):
        CGREEN = '\33[92m'
        CEND = '\33[0m'
        cmd = comando
        print(f'cmd: {cmd}')
        cmd = cmd.replace('baixar arquivo:','')
        # pega o nome do arquivo
        nome_arquivo = cmd[:cmd.find('-')]

        #Criar uma conexão TCP com um node através do seu ID e baixar o arquivo requisitado
        self.cliente_socket.sendto(str(comando).encode("utf-8"), (self.host, self.port))
        tcp = conexao_tcp_cliente()
        tcp.settimeout(3.0)
        
        with open(str(nome_arquivo), 'wb') as f:
        # print('Arquivo aberto')
            while True:
                try:
                    data = tcp.recv(1024) 
                    if not data:
                        break                 
                    f.write(data)   
                except socket.timeout:
                    print('timeout (solicita_arquivo')
                    break
        tcp.close()
        f.close()
        print(f'{CGREEN}Download do arquivo {nome_arquivo} com sucesso{CEND}')

def print_menu():
    CBLUE_FUNDO = '\33[104m'
    CEND = '\33[0m'
    print('-*'* 10 + f' {CBLUE_FUNDO}COMANDOS{CEND} '+ '-*'* 10)
    print('Lista de pares conectados: conexoes')
    print('Procurar arquivo:          procurar arquivo:nome.formato')
    print('Baixar arquivo:            baixar arquivo:nome.formato-ID')
    print('Pedir listas de arquivos:  lista arquivos')
    print('Listar nodes da rede:      usuarios')
    print('Fechar programa:           exit')
    print('limpar terminal:           clear')

def main():
    # para limpar o terminal assim que iniciar o programa
    print("\x1b[2J\x1b[1;1H")
    # para cor azul
    CBLUE = '\33[36m'
    # para cor amarela
    CYELLOW = '\33[93m'
    # para cor vermelha
    CRED = '\33[91m'
    # para cor branca de fundo
    CBRANCA_FUNDO = '\33[7m'
    # para finalizar princo color
    CEND = '\33[0m'
    comando = ''
    lista_arquivos = meus_arquivos()

    server = Servidor()
    start_new_thread(server.espera_conexoes,())

    cliente = Cliente()   

    print(f'{CBRANCA_FUNDO}ID node{CEND}: {id}\n')
    print(f'{CYELLOW}Meus arquivos{CEND}: {lista_arquivos}\n')
    #print_menu()

    while True:
        comando = input(f'{CBLUE}p2p>{CEND} ')

        if 'meus arquivos' in comando:
            # salva muma lista os nomes dos arquivos no diretorio
            lista_arquivos = meus_arquivos()
            print(f'{CYELLOW}Meus arquivos{CEND}: {lista_arquivos}\n')
            comando = ''

        if 'comandos' in comando:
            print_menu()
            comando = ''

        # ex: procurar_arquivo:vasco.jpg
        if 'procurar arquivo' in comando:
            nome_arquivo_proc = comando.replace('procurar arquivo:','')
            lista_arquivos = meus_arquivos()
            if nome_arquivo_proc in lista_arquivos:
                print(f'{CRED}Você já possui o arquivo{CEND} {nome_arquivo_proc}\n')
            else:
                cliente.procurar_arquivo(comando)
            comando = ''
        
        # ex: baixar_arquivo:vasco.jpg-ID
        if 'baixar arquivo' in comando:
            cliente.solicita_arquivo(comando)
            comando = ''
        # para pedir lista de arquivos de todos os servidores ativos
        if comando == 'lista arquivos':
            cliente.pedir_listas_arquivos(comando)
            comando = ''

        if comando == 'usuarios':
            cliente.pedir_usuarios()
            print(f'{CYELLOW}Lista de Nodes na rede{CEND}: {connections}\n')
            comando = ''

        if comando == 'meu id':
            print(f'{CBRANCA_FUNDO}ID node{CEND}: {id}\n')
            comando = ''

        if comando == 'exit':
            exit(0)

        if comando == 'clear':
            comando = ''
            print("\x1b[2J\x1b[1;1H")
        else:
            pass
        time.sleep(1)

 
        
if __name__ == '__main__':
   main()
