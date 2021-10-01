import socket
import threading
from _thread import *
import os
from datetime import datetime
import time

ip_jv = '192.168.100.8'

def sendMessage(connection):
    while True:
        mensagem = input()
        connection.send(str.encode(mensagem))

class Servidor:
    port = 60000
    host = 'localhost'
    connections = [] #lista de pares

    def __init__(self):
        self.serverUDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverUDPsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # dica da prof
        self.serverUDPsocket.bind(('', self.port)) 

    def run(self):
        print ('Aguardando conectar com outros pares...')
        while True:
            connection, endereco_cliente = self.sock.accept() # Aceita par
            self.connections.append(connection)
            print('Conectado ao par:',str(endereco_cliente))
            start_new_thread(sendMessage,(connection,))
            print("rodando")
            time.sleep(3)

    def run_udp(self):
        while(True):
            mensagem, sourceAddress = self.serverUDPsocket.recvfrom(128)
            print("Mensagem de %s is %s"%(sourceAddress, mensagem.decode("utf-8")))
            response = "Recebido"
            self.serverUDPsocket.sendto(response.encode(), sourceAddress)

    def listar_arquivos(self):
        lista = os.listdir()
        return lista

    def escreve_log(palavra, filename):
        f = open(filename, "a")
        f.write("{0} -- {1}\n".format(datetime.now().strftime("%d-%m-%Y %H:%M"), palavra))
        f.close()

    def local_ip():
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip

    def ter_arquivo(filename):
        if filename in os.listdir():
            return True
        else:
            return False

    def envia_arquivo(filename):
        pass

class Cliente:
    port = 60000
    host = '255.255.255.255'
    
    def __init__(self):
        self.ClienteUDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);

    def broadcast(self):
        self.ClienteUDPsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.ClienteUDPsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True:
            self.ClienteUDPsocket.sendto('This is a test'.encode("utf-8"), (self.host, self.port))
            #self.ClienteUDPsocket.sendto("mandei fodase".encode(), (self.host,self.port));
            response = self.ClienteUDPsocket.recv(1024)
            print(response)
            time.sleep(5)

    def listar_usuarios():
        pass

    def listar_arquivos():
        pass

    def procurar_arquivo():
        pass

    def baixar_arquivo():
        pass
    
    def pedir_arquivo(self,nome_arquivo):
        while True:
            resposta = self.sock.recv(1024)
            print(resposta.decode("utf-8"))

    def teste_t(self):
        while True:
            resposta = self.sock.recv(1024)
            print(resposta.decode("utf-8"))
            time.sleep(2)


def main_teste():

    server = Servidor()
    t_server = threading.Thread(target=server.run())
    t_server.start()
    print("teste")

    cliente = Cliente()
    t_cliente = threading.Thread(target=cliente.teste_t())
    t_cliente.start()


def main():
    entrada = input()

    if entrada == 'server':
        server = Servidor()
        t_server = threading.Thread(target=server.run_udp())
        t_server.start()
        
    elif entrada == 'cliente':
        cliente = Cliente()
        t_cliente = threading.Thread(target=cliente.broadcast())
        t_cliente.start()
    else:
        pass    
        
if __name__ == '__main__':
   main()



        
