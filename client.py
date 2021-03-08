import socket
import random
import os
word_lenght = 85

def bytes_to_int(data): #превращает строку байтов в массив чисел по 85 бит
    bit_strings = '' 
    for one_byte in data:
        for i in range(8):
            if(one_byte & (1 << i)):
                bit_strings += '1'
            else: 
                bit_strings += '0'
    res = []
    for word in (bit_strings[_:_ + word_lenght] for _ in range(0, len(bit_strings), word_lenght)):
        num = 0
        for i in range(len(word)):
            num |= int(word[i] == '1') << i
        res.append(num)
    return res
            
def hamming_encoding(in_word): #кодирование Хэмминга
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
            
def encoding_arr(arr): #кодирует массив чисел кодом хэмминга 
    ham_arr = []
    for x in arr:
        ham_arr.append(hamming_encoding(x))
    return ham_arr

def bug_count_gen(): #генерирует число ошибок
    x = random.randint(0, 100)
    if x < 70:
        return 0
    if x < 95:
        return 1
    return 2

def bug_gen(arr):  #генерирует ошибки в закодированном массиве чисел   
    count = [0,0,0]
    bugs = []
    ind = list(range(word_lenght + 14))
    for x in arr:
        random.shuffle(ind)
        ty = bug_count_gen()
        count[ty] += 1
        if ty == 0:
            bugs.append(x)
        elif ty == 1:
            bugs.append(x ^ (1 << ind[0]))
        else:
            x ^= 1 << ind[0]
            x ^= 1 << ind[1]
            bugs.append(x)
    return bugs, count

def unit_count(x): #считает число единиц в числе
    count = 0
    pow = 1
    while(pow <= x):
        if(pow & x):
            count+= 1
        pow *= 2
    return count

def sender(client, data): #отправляет данные парами пакетов
    for chunk in (data[_:_+ 13] for _ in range(0, len(data), 13)):
        client.send(len(chunk).to_bytes(2, "big"))
        client.send(chunk)
    client.send(b"\x00\x00")

def reader(path):  #считывает данные, кодирует, генерирует баги
    file_ = open(path, "r", encoding="utf-8")
    text = file_.read().encode()
    #text = "dcecdeecEECEfcneicuiejicdomeiomxcoiemcoemcoekmiec ".encode()
    print("Encoding is started")
    bit_strings = bytes_to_int(text)
    code = encoding_arr(bit_strings)
    res, cnt = bug_gen(code)
    bytes_string = b''
    for x in res:
        bytes_string += (x << 4).to_bytes(13, "big")
    print("Words with: ")
    print("0 bugs", cnt[0])
    print("1 bugs", cnt[1])
    print("2 bugs", cnt[2])
    return bytes_string
    
client = socket.socket()
client.connect(('localhost', 1573))   
print("Sending...")
sender(client, reader("text.txt"))
data = client.recv(1024)
print("result")
print(data.decode())
client.close()
os.system("pause")