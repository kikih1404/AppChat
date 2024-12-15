import socket
from threading import Thread

import rsa 
HEADER_LENGTH = 128
client_socket = None

my_public_key, my_private_key = rsa.generar_llaves()
# Connects to the server(menghubungkan ke server)
def connect(ip, port, my_username, error_callback):

    global client_socket, my_public_key

        # Buat soket
        # socket.AF_INET - keluarga alamat, IPv4, beberapa yang lain mungkin adalah AF_INET6, AF_BLUETOOTH, AF_UNIX
        # socket.SOCK_STREAM - TCP, berbasis koneksi, socket.SOCK_DGRAM - UDP, tanpa koneksi, datagram, socket.SOCK_RAW - paket IP mentah
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # hunugkan ke ip dan port
        client_socket.connect((ip, port))
    except Exception as e:
        # kesalahan koneksi
        error_callback('Connection error: {}'.format(str(e)))
        return False

    # Siapkan nama pengguna dan header lalu kirimkan
    # Kita perlu mengodekan nama pengguna ke byte, lalu menghitung jumlah byte dan menyiapkan header dengan ukuran tetap, yang juga kita enkode ke byte
    username = my_username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + username)

    # Siapkan kunci publik dan header lalu kirimkan
    # Kita perlu mengodekan nama pengguna ke byte, lalu menghitung jumlah byte dan menyiapkan header dengan ukuran tetap, yang juga kita enkode ke byte
    public_key = repr(my_public_key).encode('utf-8')
    public_key_header = f"{len(public_key):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(public_key_header + public_key)

    return True

# Mengirim pesan ke server
def send(message,user):
    print(f'\nMessage text: \n{message}\n')
    # Enkode pesan ke byte, siapkan header dan ubah ke byte, seperti nama pengguna di atas, lalu kirim
    cipher = rsa.cifrar(message, user['key'])
    print(f'\nCipher text: \n{cipher}\n')
    message = (cipher + ':>>>:' +  user['user']).encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')

    client_socket.send(message_header + message)

# Memulai fungsi mendengarkan dalam thread
#incoming_message_callback - panggilan balik yang akan dipanggil saat pesan baru tiba
#error_callback - panggilan balik yang akan dipanggil saat terjadi kesalahan
def start_listening(incoming_message_callback, error_callback):
    Thread(target=listen, args=(incoming_message_callback, error_callback), daemon=True).start()
    

# Mendengarkan pesan masuk
def listen(incoming_message_callback, error_callback):
    global my_private_key
    while True:

        try:
            # Sekarang kita ingin mengulang pesan yang diterima (mungkin ada lebih dari satu) dan mencetaknya
            while True:
                
                # Terima "header" kami yang berisi panjang nama pengguna, ukurannya ditentukan dan konstan
                new_header = client_socket.recv(HEADER_LENGTH)
                
                # Jika kami tidak menerima data, server menutup koneksi dengan baik, misalnya menggunakan socket.close() atau socket.shutdown(socket.SHUT_RDWR)
                if not len(new_header):
                    error_callback('Connection closed by the server')

                # Ubah header menjadi nilai int
                username_length = int(new_header.decode('utf-8').strip())

                # Terima dan dekode nama pengguna
                username = client_socket.recv(username_length).decode('utf-8')
                
                # Sekarang lakukan hal yang sama untuk pesan (karena kami menirima nama pengguna, kami menerima seluruh pesan, tidak perlu memeriksa apakah ada panjangnya)
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                
                if username != '__flag__':
                    cipher = client_socket.recv(message_length).decode('utf-8')
                    print(f'\nCipher text: \n{cipher}\n')
                    message = rsa.descifrar(cipher, my_private_key)
                    print(f'\nDeciphered text: \n{message}\n')
                else: 
                    message = client_socket.recv(message_length).decode('utf-8')

                # Print pesan
                
                incoming_message_callback(username, message)

        except Exception as e:
            # Pengecualian lainnya - sesuatu terjadi, keluar
            error_callback('Reading error: {}'.format(str(e)))