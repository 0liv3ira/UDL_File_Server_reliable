import socket
import time
import sys
import os

#Dados servidor
porta_udp = 10000
porta2 = 30000
udp_ip = '127.0.0.1'
senha = "admin"

#Dados Cliente
ip_cliente = "127.0.0.1"
porta_cliente = 20000

# definindo tamanho do pacote
PACKET_SIZE = 1024

# definindo timeout em segundos
TIMEOUT = 5

# definindo janela de envio e recebimento
WINDOW_SIZE = 4

def verifica_senha(senha_recebida):
    if senha_recebida == senha:
        return True
    else:
        return False

def Listar_arquivos():
    print("Enviando mensandem de confirmação...")
    mensagem = "Listando Arquivos"
    mensagemEncoded = mensagem.encode("utf-8")
    conexao.sendto(mensagemEncoded, cliente_addr)
    Diretorio = os.listdir(path=r'C:\Users\deoli\OneDrive\Área de Trabalho\Trabalho_Redes_2\arquivos') #Lista arquivos do diretório
    lista = []
    for arquivo in Diretorio:
        lista.append(arquivo)
    lista_encoded = str(lista).encode("utf-8")
    conexao.sendto(lista_encoded, cliente_addr)

def envia_arquivo(filename, ip, port):

    path='C:/Users/deoli/OneDrive/Área de Trabalho/Trabalho_Redes_2/arquivos/' + filename

    # criando socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    # lendo arquivo
    with open(path, "rb") as f:
        file_data = f.read()
    print(file_data)
    # dividindo o arquivo em pacotes
    packets = [file_data[i:i+PACKET_SIZE] for i in range(0, len(file_data), PACKET_SIZE)]

    # enviando pacotes
    seq_num = 0
    ack_num = 0
    while seq_num < len(packets):
        # enviando janela de pacotes
        for i in range(seq_num, min(seq_num+WINDOW_SIZE, len(packets))):
            packet = bytearray()
            packet.extend(seq_num.to_bytes(4, byteorder="big"))
            packet.extend(packets[i])
            sock.sendto(packet, (ip, port))

        # recebendo pacotes de confirmação
        try:
            while True:
                ack_packet, address = sock.recvfrom(PACKET_SIZE)
                ack_num = int.from_bytes(ack_packet[:4], byteorder="big")
                if ack_num >= seq_num:
                    break
        except socket.timeout:
            pass

        # atualizando número de sequência
        seq_num = ack_num + 1

    # fechando conexão
    sock.close()

def receber_arquivo(filename, ip, port):

    # criando socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    sock.settimeout(TIMEOUT)

    # recebendo pacotes
    received_packets = {}
    while True:
        try:
            packet, address = sock.recvfrom(PACKET_SIZE)
            seq_num = int.from_bytes(packet[:4], byteorder="big")
            received_packets[seq_num] = packet[4:]
            ack_packet = seq_num.to_bytes(4, byteorder="big")
            sock.sendto(ack_packet, address)
        except socket.timeout:
            pass

        # verificando se todos os pacotes foram recebidos
        if len(received_packets) == seq_num + 1:
            break

    # salvando arquivo

    path='C:/Users/deoli/OneDrive/Área de Trabalho/Trabalho_Redes_2/arquivos/' + filename

    with open(path, "wb") as f:
        for i in range(len(received_packets)):
            print(received_packets)
            f.write(received_packets[i])

    # fechando conexão
    sock.close()


try:
    conexao = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    conexao.bind((udp_ip, porta_udp))
    print("Porta aberta com sucesso. Aguardando o cliente se conectar.")
except socket.error:
    print("Erro em abrir a porta")
    sys.exit(1)

while True:
    try:
        data, cliente_addr = conexao.recvfrom(4096)
    except ConnectionResetError:
        print("Erro, numero da porta diverge") 
        sys.exit()
    
    texto = data.decode("utf-8")
    decompor_texto = texto.split()
    if verifica_senha(decompor_texto[0]):
        if decompor_texto[1] == "get":
            envia_arquivo(decompor_texto[2], ip_cliente, porta_cliente)  # Nome do arquivo, ip do cliente, porta do cliente
        elif decompor_texto[1] == "put":
            receber_arquivo(decompor_texto[2], udp_ip, porta2)
        elif decompor_texto[1] == "list":           
            Listar_arquivos()

        elif decompor_texto[1] == "exit":
            pass
        else:
            pass

    else:
        print("Senha está errada")
        pass
