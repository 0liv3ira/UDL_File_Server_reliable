import socket
import sys
import struct

# definindo tamanho do pacote
PACKET_SIZE = 1024

# definindo timeout em segundos
TIMEOUT = 5

# definindo janela de envio e recebimento
WINDOW_SIZE = 4

#Dados do servidor
ip_servidor = "127.0.0.1"
porta = 10000
porta2 = 30000
#dados do cliente
ip_cliente = "127.0.0.1"
porta_cliente = 20000

def listar():
    print("Aguardando confirmação")
    try:
        dados , clienteAddr = conexao.recvfrom(51200)
    except ConnectionResetError:
        print("Erro")
        sys.exit()
    
    texto = dados.decode("utf-8")
    print(texto)

    if texto == "Listando Arquivos":
        dados2, clienteAddr2 = conexao.recvfrom(4096)
        texto2 = dados2.decode("utf-8")
        print(texto2)
    else:
        pass

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
    with open(filename, "wb") as f:
        for i in range(len(received_packets)):
            print(received_packets)
            f.write(received_packets[i])

    # fechando conexão
    sock.close()

def envia_arquivo(filename, ip, port):

    # criando socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    # lendo arquivo
    with open(filename, "rb") as f:
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

try:
    conexao = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Socket cliente inicializadndo ...")
except socket.error:
    print("Falha em criar o socket cliente")
    sys.exit()

while True:
    comando = input("Digite o comando no seguinte formato - senha - comando (get/put/list/exit) - nome do arquivo ( Se necessário ) seu IP e Porta\n") 
    aux_comando = comando.encode('utf-8')

    try:
        conexao.sendto(aux_comando, (ip_servidor, porta))
    except ConnectionResetError:
        print("Falha em enviar")
        sys.exit()

    comando_split = comando.split()

    if comando_split[1] == "get":
        receber_arquivo(comando_split[2],ip_cliente,porta_cliente)

    if comando_split[1] == "put":
        envia_arquivo(comando_split[2],ip_servidor,porta2)

    if comando_split[1] == "list":
        listar()

    if comando_split[1] == "exit":
        pass
