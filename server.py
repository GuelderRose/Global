import socket
word_lenght = 85

def hamming_encoding(in_word): 
    out_word = in_word
    for i in range(word_lenght):
        bit = 0
        if(out_word & (1 << i)):
            bit = 1
        if(bit):
            for len in range(8):
                sz = 1 << len
                out_word ^= 1 << (word_lenght + (i // sz) % 2 + 2 * len)
    return out_word

def unit_count(x): #считает число единиц в числе
    count = 0
    pow = 1
    while(pow <= x):
        if(pow & x):
            count+= 1
        pow *= 2
    return count

def decoding_word(x): #раскодирует число проверяя на наличие багов
    x >>= 4
    nx = x
    for i in range(15):
        if nx & (1 << (word_lenght + i)):
            nx ^= 1 << (word_lenght + i)
    y = nx
    nx = hamming_encoding(nx)
    if(nx == x):
        return 0
    if unit_count(x ^ nx) == 1:
        return 1
    mask = (1 << word_lenght) - 1
    for i in range(15):
        curmask = 0
        if (nx & (1 << (i + word_lenght))) != (x & (1 << (i + word_lenght))):
            len = 1 << (i // 2)
            for pos in range(i % 2 * len, word_lenght, 2 * len):
                for j in range(len):
                    curmask |= 1 << (pos + j)
            mask &= curmask
    y ^= mask
    y = hamming_encoding(y)
    if(unit_count(y^x) == 1):
        return 1
    return 2

def array_decoding(arr): #раскодирует массив, подсчитывая статистику по количеству багов
    count = [0, 0, 0]
    for x in arr:
        count[decoding_word(x)] += 1
    return count

def read_data(connection):  #считывание данных парами (длина предстоящего пакета - сам пакет)
    res = []
    while True:
        part_lenght = int.from_bytes(read_byte_num(connection, 2), "big")
        if part_lenght == 0:
            return res
        res.append(int.from_bytes(read_byte_num(connection, part_lenght), "big"))
    return res

def read_byte_num(connection, bytes_count): #считывание строгого количества байт из потока
    bytes_ = b''
    while len(bytes_) < bytes_count: 
        part = connection.recv(bytes_count - len(bytes_)) 
        if not part:
            raise IOError("Connection lost")
        bytes_ += part
    return bytes_

server = socket.socket()
server.bind(('Localhost', 1573))
server.listen(1)

while True:
    connection, address = server.accept()
    print('Connected:', address)
    data = read_data(connection)
    print("Decoding is started")
    count_ = array_decoding(data)
    print("Result", count_, end="\n\n")
    connection.send(str(count_).encode())
    connection.close()

