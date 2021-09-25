
import os
import socket 
import threading 
import sys
import time
from random import randint
from timeit import default_timer as timer

BYTE_SIZE = 2048
HOST = '127.0.0.1'
PORT = 5000
PEER_BYTE_DIFFERENTIATOR = b'\x11' 
RAND_TIME_START = 1
RAND_TIME_END = 2
REQUEST_STRING = "req"

############################ SERVER #####################################
class Server: 

    #  construtor
    def __init__(self, msg):
        try:
            # the message to upload in bytes
            self.msg = msg

            # define um socket
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # permite que varios processos (e seus respectivos sockets) se associem a mesma porta de uma maquina. 
            # Para  evitar erros no bind
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.connections = []

            # cria uma lista de pontos 
            self.peers = []

            # fornece a porta/sokcet a um processo
            self.s.bind((HOST, PORT))

            # lista para conexao
            self.s.listen(1)

            print("-"*12 + " Rodando o Servidor " + "-"*12)
            
            self.run()
        except Exception as e:
            sys.exit()



    """
    Este método trata do envio de informações aos clientes
    Este método também fecha a conexão se o cliente saiu
    : param: conexão -> O servidor de conexão está conectado a
    : param: a -> (endereço ip, porta) do sistema conectado
    """
    def handler(self, connection, a):
        
        try:
            while True:
                # servidor recebe a mensagem
                data = connection.recv(BYTE_SIZE)
                for connection in self.connections:
    
                    # O par que está conectado deseja se desconectar
                    if data and data.decode('utf-8')[0].lower() == 'q':

                        # desconecta o par
                        self.disconnect(connection, a)
                        return

                    elif data and data.decode('utf-8') == REQUEST_STRING:
                        print("-"*12 + " UPLOADING " + "-"*12)
                        # se a conexão ainda estiver ativa, enviamos de volta os dados
                        # esta parte trata do upload do arquivo
                        connection.send(self.msg)
                        #convert_to_music(self.msg)
        except Exception as e:
            sys.exit()


    """
        Este metodo e executado quando o usuario desconecta
    """
    def disconnect(self, connection, a):
        self.connections.remove(connection)
        self.peers.remove(a)
        connection.close()
        self.send_peers()
        print('f{a}, foi desconectado')
        print("-" * 12)



    """
        Este metodo e usado para executar o servidor
        Este metodo cria um tópico diferente para cada cliente
    """
    def run(self):
        # constantly listeen for connections
        while True:
            connection, a = self.s.accept()

            # append to the list of peers 
            self.peers.append(a)
            print(f'Os pares sao: {self.peers}')
            self.send_peers()
            # cria thread para conexao
            c_thread = threading.Thread(target=self.handler, args=(connection, a))
            c_thread.daemon = True
            c_thread.start()
            self.connections.append(connection)
            print(f'{a}, conectado')
            print("-" * 12)



    """
        envia uma lista de pares para todos os pares que estão conectados ao servidor
    """
    def send_peers(self):
        peer_list = ''
        for peer in self.peers:
            peer_list = peer_list + str(peer[0]) + ','

        for connection in self.connections:
            # adicionamos um byte '\ x11' no início do nosso byte 
            # Desta forma podemos diferenciar se recebemos uma mensagem ou uma lista de pares
            data = PEER_BYTE_DIFFERENTIATOR + bytes(peer_list, 'utf-8')
            connection.send(PEER_BYTE_DIFFERENTIATOR + bytes(peer_list, 'utf-8'))

#####################################################################


############################ CLIENT #####################################

class Client: 

    def __init__(self, addr):
       # cria o socket e define se e UDP ou TCP
       #lembrar de fechar o socket depois
       self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

       # allow python to use recently closed socket
       self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

       # make the connection
       self.s.connect((addr, PORT))

       self.previous_data = None
    
       # create to work on a different thread
       i_thread = threading.Thread(target=self.send_message)
       i_thread.daemon = True
       i_thread.start()

       # send the message requesting data

    

       while True:

           r_thread = threading.Thread(target=self.recieve_message)
           r_thread.start()
           r_thread.join()

           data = self.recieve_message()

           if not data:
               # means the server has failed
               print("-" * 12 + " Servidor falhou " + "-" * 12)
               break

           elif data[0:1] == b'\x11':
               print("possui pares")
               # first byte is the byte '\x11 we added to make sure that we have peers
               self.update_peers(data[1:])




    """
        This thread will deal with printing the recieved message
    """
    def recieve_message(self):
       try:
           print("Recebendo -------")
           data = self.s.recv(BYTE_SIZE)

           print(data.decode("utf-8"))

           print('\nA mensagem recebida do lado do cliente foi: ')

           if self.previous_data != data:
               create_file(data, new_file_path)
               self.previous_data = data
           # download the file to the computer
            
           return data
       except KeyboardInterrupt:
           self.send_disconnect_signal()


    """
        This method updates the list of peers
    """
    def update_peers(self, peers):
        # our peers list would lool like 127.0.0.1, 192.168.1.1, 
        # we do -1 to remove the last value which would be None
        self.peers = str(peers, "utf-8").split(',')[:-1]
    

    """
        This method is used to send the message
        :param: msg -> The optional message to send 
    """
    def send_message(self):
        try:
            #while True:
                # sleep for a little bit as to for the main thread to run
                #data = input("Please enter a message: ")

                # encode the message into bytes
                # other code will run when this happens as the thread is busy
                # request to download the file
            self.s.send(REQUEST_STRING.encode('utf-8'))

                # check if the user wants to quit the connection
                #if data[0:1].lower() == "q":
                #    self.send_disconnect_signal()

        except KeyboardInterrupt as e:
            # If a user turns the server off due to KeyboardInterrupt
            self.send_disconnect_signal()
            return




    def send_disconnect_signal(self):
       print("Desconectando do servidor")
       # signal the server that the connection has closed
       self.s.send("q".encode('utf-8'))
       self.exit()
######################################################################

###################### PARTE DE ARQUIVOS ######################################

# cwd = os.getcwd()
# path_to_file = cwd + "/read_file.txt"
# new_file_path = cwd + "/new_file.txt"

def convert_to_bytes(file_path):
    read_data = None
    with open(file_path, 'r') as file:
        read_data = file.read()
    return read_data.encode('utf-8')



def create_file(data, new_file_path):
    data = data.decode('utf-8')
    print('Gravando em arquivo')
    with open(new_file_path, 'w') as file:
        file.write(data)
    return True


def main_file(path_to_file, new_file_path):
    data = convert_to_bytes(path_to_file)
    create_file(data, new_file_path)

########################################################################

###################### P2P #############################################

class p2p:
    # make ourself the default peer
    peers = ['127.0.0.1']


# def main():
#     # if the server breks we try to make a client a new server
#     #msg = convert()


#     msg = convert_to_bytes()
#     while True:
#         try:
#             print("-" * 21 + " Tentando se conectar " + "-" * 21)
#             # sleep a random time between 1 -5 seconds
#             time.sleep(randint(RAND_TIME_START,RAND_TIME_END))
#             for peer in p2p.peers:
#                 try:
#                     cliente = Client(peer)
#                 except KeyboardInterrupt:
#                     sys.exit(0)
#                 except:
#                     pass


#                 # become the server
#                 try:
#                     server = Server(msg)
#                 except KeyboardInterrupt:
#                     sys.exit()
#                 except:
#                     pass

#         except KeyboardInterrupt as e:
#             sys.exit(0)

########################################################################

###################### FUNCOES UTEIS #############################################
# abre diretorio
def AbreDiretorio(path):
    os.chdir(path)

# salva arquivos do diretorio numa lista
def ListaArquivos():
    return os.listdir()

# returna a str do nome do arquivo que o usuario escolher
def EscolheArquivo(list_arq):
    cont = 0
    print('Escolha o arquivo para Download \n')
    for arquivo in list_arq:
        print(f'[{cont}]- {arquivo}')
        cont+=1
    indice = int(input('Informe o numero do arquivo: '))
    print(f'O arquivo escolhido foi {list_arq[indice]}')
    return list_arq[indice]
    
# funcao para enviar o nome do arquivo selecionado para o servidor
# param: cliente -> recebe instancia do cliente apos se conectar o servidor, ou seja, apos  ('cient.connect(HOST, PORT))
def NomeArquivo(cliente, list_arq):
    # salva a str com o nome do arquivo que o cliente deseja baixar
    namefile = EscolheArquivo(list_arq)
    # envia para servidor o nome do arquivo que o cliente deseja fazer dowload
    cliente.send(namefile.encode())

"""
    Esta funcao retorna True caso timeout seja atingido
    param: segundos -> tempo em segundos para gerar timeout
"""
def TimeOut(segundos):
    start = timer()
    while True:
        if timer() - start >= segundos:
            # start = timer()
            return True


######################################################################################

if __name__ == "__main__":

    # cwd = os.getcwd()
    path_to_file = 'C:\\Users\\ernes\\Desktop\\redes\\trab1\\develop\\teste1.txt'
    new_file_path = 'C:\\Users\\ernes\\Desktop\\redes\\trab1\\develop\\novo.txt'
    main_file(path_to_file, new_file_path)
    
    msg = convert_to_bytes(path_to_file)
    while True:
        try:
            print('-' * 12 + 'Tentando se conectar' + '-' *12)
            # sleep a random time between 1 -5 seconds
            time.sleep(randint(RAND_TIME_START,RAND_TIME_END))
            for peer in p2p.peers:
                try:
                    print('Cliente\n')
                    cliente = Client(peer)
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    pass


                # become the server
                try:
                    print('Servidor\n')
                    server = Server(msg)
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    pass

        except KeyboardInterrupt as e:
            sys.exit(0)

#___________________________________________________

