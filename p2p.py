import socket
from _thread import *
import os
from datetime import datetime
import time
import pickle
import random
from timeit import default_timer as timer
import sys

connections = []
id = str(random.randint(1,1000))

# funcao para retornar tamanho de um arquivo em Bytes
def getSize(filename):
    st = os.stat(filename)
    return st.st_size
# funcao que salva muma lista os nomes dos arquivos no diretorio
def meus_arquivos():
    # guarda o diretorio onde o prog esta rodando
    dir = os.path.dirname(os.path.realpath(__file__))
    # abre diretorio
    os.chdir(dir)
    return os.listdir()

# funcao que envia lista de arquivos no diretorio corrente do prog
def enviar_lista_arquivos(connection):
    data=pickle.dumps(meus_arquivos())
    connection.send(data)

# funcao que realiza a conexao TCP da parte servidor
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

# funcao para escrever o log num arquivo .txt
def escreve_log(palavra, filename='log.txt'):
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
         
    # metodo que espera solicitacoes e conexoes de clientes na rede
    def espera_conexoes(self):
        # para cor vermelha
        CRED = '\33[91m'
        # para finalizar print color
        CEND = '\33[0m'
        while(True):
            mensagem, sourceAddress = self.server_socket.recvfrom(128)
            # descomentar linha abaixo para depurar solicitacoes que o servidor recebe
            # print("conectado com %s, mensagem: %s"%(sourceAddress, mensagem.decode("utf-8")))
            mensagem_decode = mensagem.decode("utf-8")
            id_c = mensagem_decode[0:mensagem_decode.find('-')]
            mensagem_decode = mensagem_decode[mensagem_decode.find('-')+1:]

            if 'procurar arquivo' in mensagem_decode: 
                nome_arquivo = mensagem_decode.replace('procurar arquivo:','') # pega só o nome do arquivo

                lista_arquivos = meus_arquivos()
                if nome_arquivo in lista_arquivos:
                    try:
                        # abre o arquivo para descobrir seu tamanho e enviar junto com o id
                        file = open(nome_arquivo,'rb')
                        tamanho_file = f', tamanho: {getSize(nome_arquivo)} Bytes'
                        file.close()
                        con,cliente,tcp = conexao_tcp_server()
                        con.send(str.encode('ID: '+ id + tamanho_file))
                        con.close()
                        tcp.close()
                        escreve_log('Pesquisa de arquivo, node: '+id_c)                       
                    except socket.timeout:
                        print(f'Timeout (espera_conexoes -> procurar arquivo)')
                        pass
                    except:
                        pass

            elif 'listar arquivos' in mensagem_decode:
                # pegar o ID
                num_id = mensagem_decode.replace('listar arquivosID:','') # pega só ID
                # verificar se e o ID solicitado
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
                        escreve_log('Listagem de arquivos, node:'+id_c)                   
                    except socket.timeout:
                        print(f'Timeout (espera_conexoes -> listar arquivos)')
                        pass
                    except:
                        pass

            elif 'pedir_IDs' in mensagem_decode:
                try:
                    con,cliente,tcp = conexao_tcp_server()
                    con.send(str.encode(id))
                    con.close()
                    tcp.close()
                    escreve_log('Pedido de ID, node:'+id_c)    
                 
                except socket.timeout:
                    print(f'Timeout (espera_conexoes -> pedir_IDs)')
                    pass
                except:
                    pass

            elif 'baixar arquivo' in mensagem_decode:
                mensagem_decode = mensagem_decode.replace('baixar arquivo:','') # pega só nome do arquivo e ID
                num_id = mensagem_decode[mensagem_decode.find('-')+1:]
                nome_arquivo = mensagem_decode[:mensagem_decode.find('-')]

                

                if num_id == id:
                    con,cliente,tcp = conexao_tcp_server()

                    file = open(nome_arquivo,'rb')
                    inicio = time.time()
                    con.sendfile(file, offset=0, count=None)
                    print(f'Enviados {file.tell()} Bytes para Node {id_c}')
                    con.close()
                    tcp.close() 
                    file.close()
                    fim = time.time()
                    tempo_total = str(fim-inicio)
                    escreve_log('Envio do arquivo '+nome_arquivo+', tempo total: '+tempo_total+' s, Node:'+id_c)

                    print('Envio de arquivo concluído\n')
            else:
                print(f'{CRED}Comando invalido!{CEND}')
                print('Para lista de comandos digite: comandos')

    def local_ip():
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip


# funcao para mostrar uma lista no terminal
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
    return tcp


class Cliente:
    port = 60000
    host = '255.255.255.255' # para mandar broadcast
    cliente_socket = socket.socket()
    def __init__(self):
        self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cliente_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.cliente_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # metodo para pedir IDs dos Nodes ativos e salvar
    def pedir_usuarios(self):
        self.cliente_socket.sendto(str(id+'-pedir_IDs').encode("utf-8"), (self.host, self.port))
        connections.clear()
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
            print(f'Timeout (pedir_usuarios)')
            pass
        except:
            pass

    # metodo para pedir e salvar a lista de arquivos de cada Node
    def pedir_listas_arquivos(self,mensagem):
        # Solicita via BROADCAST a lista arquivos de cada usuário na rede
    
        # comando de cores
        CYELLOW = '\33[93m'
        CEND = '\33[0m'

        # para atualizar a lista de usuarios
        self.pedir_usuarios()
        try: 
            for id in connections:
                try:
                    # pedido de arquivo com o ID de um servidor
                    self.cliente_socket.sendto(str(id +'-'+ mensagem + f'ID:{id}').encode("utf-8"), (self.host, self.port))
                    tcp = conexao_tcp_cliente()
                    tcp.settimeout(1.0)
                    msg = tcp.recv(1024)
                    lista_recebida=pickle.loads(msg)
                    # ordenar os nomes
                    lista_recebida = sorted(lista_recebida)
                    
                    tcp.close()
                    time.sleep(0.3)
                    tcp2 = conexao_tcp_cliente()
                    msg_id = tcp2.recv(1024)
                    id_rcv = msg_id.decode('utf-8')
                    id_rcv = id_rcv.replace('ID: ','')
                    print(f'{CYELLOW}Lista recebida do Node ID{CEND} {id_rcv}: {lista_recebida}\n')
                    tcp2.close()
                except socket.timeout:
                    break
        except socket.timeout:
            print('Nao foi possivel receber o arquivo solicitado')
            pass
        except:
            pass


    # metodo para procurar um arquivo nos Nodes ativos
    def procurar_arquivo(self,comando):
        CYELLOW = '\33[93m'
        CEND = '\33[0m'
        # Enviar broadcast com o nome de um arquivo, retornar os IDs de quem possui
        nodes_com_arq = []
        self.cliente_socket.sendto(str(id+'-'+comando).encode("utf-8"), (self.host, self.port))

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
        
        print(f'{CYELLOW}Nodes com o arquivo solicitado{CEND}: {nodes_com_arq}\n')

    # metodo que solicita um arquivo para o servidor
    def solicita_arquivo(self,comando):
        CGREEN = '\33[92m'
        CEND = '\33[0m'
        cmd = comando

        cmd = cmd.replace('baixar arquivo:','')
        # pega o nome do arquivo
        nome_arquivo = cmd[:cmd.find('-')]

        # Criar uma conexão TCP com um node através do seu ID e baixar o arquivo requisitado
        self.cliente_socket.sendto(str(id+'-'+comando).encode("utf-8"), (self.host, self.port))
        tcp = conexao_tcp_cliente()
        tcp.settimeout(3.0)
        # abre um arquivo para escrever o arquivo solicitado
        with open(str(nome_arquivo), 'wb') as f:
        
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
        print(f'{CGREEN}Download do arquivo {nome_arquivo} com sucesso!{CEND}\n')
# funcao para mostrar menu de comandos
def print_menu():
    CBLUE_FUNDO = '\33[104m'
    CEND = '\33[0m'
    print('-*'* 10 + f' {CBLUE_FUNDO}COMANDOS{CEND} '+ '-*'* 10)
    print('Descobrir o ID do prog:          meu id')
    print('Arquivos no diretorio corrente:  meus arquivos')
    print('Procurar arquivo:                procurar arquivo:nome.formato')
    print('Baixar arquivo:                  baixar arquivo:nome.formato-ID')
    print('Pedir listas de arquivos:        listar arquivos')
    print('Listar nodes da rede:            usuarios')
    print('Comandos disponiveis:            comandos')
    print('limpar terminal:                 clear')
    print('Fechar programa:                 exit\n')

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
    # para finalizar print color
    CEND = '\33[0m'
    comando = ''
    # salva lista de arquivos do diretorio corrente do prog
    lista_arquivos = meus_arquivos()
    # ativa o servidor
    server = Servidor()
    start_new_thread(server.espera_conexoes,())
    # ativa o cliente
    cliente = Cliente()   

    print(f'{CBRANCA_FUNDO}ID node{CEND}: {id}\n')
    print(f'{CYELLOW}Meus arquivos{CEND}: {lista_arquivos}\n')
    #print_menu()

    while True:
        comando = input(f'{CBLUE}p2p>{CEND} ')
        # mostra os meus arquivos no diretorio
        if 'meus arquivos' in comando:
            # salva muma lista os nomes dos arquivos no diretorio
            lista_arquivos = meus_arquivos()
            print(f'{CYELLOW}Meus arquivos{CEND}: {lista_arquivos}\n')
            comando = ''
        # lista opcoes de comando
        elif 'comandos' in comando:
            print_menu()
            comando = ''
        # procura deterinado arquivo
        # ex: procurar arquivo:vasco.jpg
        elif 'procurar arquivo' in comando:
            nome_arquivo_proc = comando.replace('procurar arquivo:','')
            lista_arquivos = meus_arquivos()
            # verifica se ja possui o arquivo que procura
            if nome_arquivo_proc in lista_arquivos:
                print(f'{CRED}Você já possui o arquivo{CEND} {nome_arquivo_proc}\n')
            else:
                cliente.procurar_arquivo(comando)
            comando = ''
        # solicita o download de determinado arquivo e determinado Node
        # ex: baixar arquivo:vasco.jpg-ID
        elif 'baixar arquivo' in comando:
            aux = comando
            # atualiza lista de usuarios
            cliente.pedir_usuarios()
            
            nome_arquivo_ID = aux.replace('baixar arquivo:','')
            num_id = aux[aux.find('-')+1:]
            nome_arquivo = nome_arquivo_ID[:nome_arquivo_ID.find('-')]
            # verifica se o ID esta errado
            if num_id not in connections:
                print(f'{CRED}ID informado para requerir arquivo invalido!{CEND}\n')
                comando = ''
                continue           
            # atualiza a lista de arquivos
            lista_arquivos = meus_arquivos()
            # tratando o caso de tentar baixar arquivo que ja possui
            if nome_arquivo in lista_arquivos:
                print(f'{CRED}Você já possui o arquivo{CEND} {nome_arquivo}\n')
            else:
                cliente.solicita_arquivo(comando)
            comando = ''

        # para pedir lista de arquivos de todos os Nodes ativos
        elif comando == 'listar arquivos':
            cliente.pedir_listas_arquivos(comando)
            comando = ''
        # mostra lista de Nodes ativos
        elif comando == 'usuarios':
            cliente.pedir_usuarios()
            print(f'{CYELLOW}Lista de Nodes na rede{CEND}: {connections}\n')
            comando = ''
        # mostra ID do Node 
        elif comando == 'meu id':
            print(f'{CBRANCA_FUNDO}ID node{CEND}: {id}\n')
            comando = ''
        # encerra o prog
        elif comando == 'exit':
            sys.exit()
        # limpa terminal
        elif comando == 'clear':
            print("\x1b[2J\x1b[1;1H")
            comando = ''          
        # caso de comando invalido
        else:           
            print(f'{CRED}Comando invalido!{CEND}')
            print('Para listar comandos digite: comandos\n')
            pass

 
        
if __name__ == '__main__':
   main()