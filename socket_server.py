import socket
import select

HEADER_LENGTH = 128

IP = socket.gethostbyname(socket.gethostname())
PORT = 1234

# Buat soket
# socket.AF_INET - keluarga alamat, IPv4, beberapa yang lain mungkin adalah AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, berbasis koneksi, socket.SOCK_DGRAM - UDP, tanpa koneksi, datagram, socket.SOCK_RAW - paket IP mentah
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - opsi soket
# SOL_ - level opsi soket
# Mengatur REUSEADDR (sebagai opsi soket) ke 1 pada soket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, jadi server memberi tahu sistem operasi bahwa ia akan menggunakan IP dan port yang diberikan
# Untuk server yang menggunakan 0.0.0.0 berarti mendengarkan semua antarmuka yang tersedia, berguna untuk terhubung secara lokal ke 127.0.0.1 dan dari jarak jauh ke IP antarmuka LAN
server_socket.bind((IP, PORT))

# Ini membuat server mendengarkan koneksi baru
server_socket.listen()

# Daftar soket untuk select.select()
sockets_list = [server_socket]

# Daftar clients yang terhubung - soket sebagai kunci, header pengguna dan nama sebagai data
clients = {}

# Daftar kunci publik - soket sebagai kunci, header pengguna dan nama sebagai data
keys = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Menangani penerimaan pesan
def receive_message(client_socket):

    try:

        # Terima "header" kami yang berisi panjang pesan, ukurannya ditentukan dan konstan
        message_header = client_socket.recv(HEADER_LENGTH)

        # Jika kami tidak menerima data, klien menutup koneksi dengan baik, misalnya menggunakan socket.close() atau socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Ubah header menjadi nilai int
        message_length = int(message_header.decode('utf-8').strip())

        # Terima pesan
        message = client_socket.recv(message_length).decode('utf-8')
        if ':>>>:' in message:
            message = message.split(':>>>:')
            message = {
                'header': message_header,
                'data': message[0].encode('utf-8'),
                'addressee': message[1]
            }
        else:
            message = {
                'header': message_header,
                'data': message.encode('utf-8')
            }
        # Mengembalikan objek header pesan dan data pesan
        return message

    except:

        # Jika kita di sini, klien menutup koneksi secara paksa, misalnya dengan menekan ctrl+c pada skripnya
        # atau baru saja kehilangan koneksinya
        #socket.close() juga memanggil socket.shutdown(socket.SHUT_RDWR) yang mengirimkan informasi tentang penutupan soket (shutdown read/write)
        # dan itu juga penyebab ketika kita menerima pesan kosong
        return False

def update_users_status():
    
    for client_socket in clients:
        others_keys = {}
        for key in keys.keys():
            if clients[client_socket]['data'] != key:
                others_keys[key.decode("utf-8")] = keys[key]
        message = repr(others_keys).encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        flag = '__flag__'.encode('utf-8')
        flag_header = f"{len(flag):<{HEADER_LENGTH}}".encode('utf-8')
        #print(message_header + message)
        client_socket.send(flag_header + flag + message_header + message)

while True:

    # Memanggil panggilan sistem Unix select() atau panggilan Windows select() WinSock dengan tiga parameter:
    # - rlist - soket yang akan dipantau untuk data masuk
    # - wlist - soket untuk data yang akan dikirim (memeriksa apakah misalnya buffer tidak penuh dan soket siap untuk mengirim beberapa data)
    # - xlist - soket yang akan dipantau untuk pengecualian (kami ingin memantau semua soket untuk kesalahan, jadi kami dapat menggunakan rlist)
    # Mengembalikan daftar:
    # - reading - soket tempat kami menerima beberapa data (dengan begitu kami tidak perlu memeriksa soket secara manual)
    # - writing - soket yang siap untuk data yang akan dikirim melalui soket tersebut
    # - errors - soket dengan beberapa pengecualian
    # Ini adalah panggilan pemblokiran, eksekusi kode akan "menunggu" di sini dan "mendapatkan" pemberitahuan jika ada tindakan yang harus diambil
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    # Ulangi socket yang diberitahukan
    for notified_socket in read_sockets:

        # Jika soket yang diberitahukan adalah soket server - koneksi baru, terima saja
        if notified_socket == server_socket:

            # Terima koneksi baru
            # Itu memberi kita soket baru - soket klien, yang terhubung ke klien yang diberikan saja, soket ini unik untuk klien tersebut
            # Objek lain yang dikembalikan adalah ip/port set
            client_socket, client_address = server_socket.accept()

            # client harus segera mengirimkan nama mereka, menerimanya
            user = receive_message(client_socket)

            # Jika Salah - klien terputus sebelum dia mengirim namanya
            if user is False:
                continue

            # client harus segera mengirimkan kunci publik mereka, menerimanya
            public_key = receive_message(client_socket)

            # Jika Salah - klien terputus sebelum dia mengirim namanya
            if public_key is False:
                continue

            public_key = eval(public_key['data'])
            #print(f'PUBLIC KEY: {public_key}')

            # Tambahkan soket yang diterima ke daftar select.select()
            sockets_list.append(client_socket)

            # Simpan juga nama pengguna dan header nama pengguna
            clients[client_socket] = user

            # Simpan juga kunci publik dan nama pengguna
            keys[user['data']] = public_key
            
            update_users_status()

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
            #print('\n', list(clients.values()))

        # Jika tidak, soket yang ada sedang mengirimkan pesan
        else:

            # Terima pesan
            message = receive_message(notified_socket)

            # Jika Salah, klien terputus, pembersihan
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Hapus dari daftar untuk kunci publik
                keys.pop(clients[notified_socket]['data'])

                # Hapus dari daftar untuk socket.socket()
                sockets_list.remove(notified_socket)

                # Hapus dari daftar pengguna kami
                del clients[notified_socket]

                update_users_status()

                continue

            # Dapatkan pengguna melalui soket yang diberitahukan, jadi kami akan tahu siapa yang mengirim pesan
            user = clients[notified_socket]


            print(f'Received message from {user["data"].decode("utf-8")}')

            # Ulangi client yang terhubung dan siarkan pesan
            for client_socket in clients:
                # Tapi jangan kirim ke pengirim
                if clients[client_socket]['data'] == message['addressee'].encode('utf-8'):

                    # Kirim pengguna dan pesan (keduanya dengan header mereka)
                    # Di sini kita menggunakan kembali header pesan yang dikirim oleh pengirim, dan header nama pengguna tersimpan yang dikirim oleh pengguna saat ia terhubung
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # Sebenarnya tidak perlu untuk memiliki ini, tetapi akan menangani beberapa pengecualian soket untuk berjaga-jaga
    for notified_socket in exception_sockets:

        # Hapus dari daftar untuk socket.socket()
        sockets_list.remove(notified_socket)

        # Hapus dari daftar pengguna kami
        del clients[notified_socket]