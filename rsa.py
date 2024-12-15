from math import gcd
import random

def generar_e(phi_n):
    e = 2
    le = []
    while e < phi_n:
        m = gcd(e, phi_n)
        if m == 1:
            le.append(e)
        e = e + 1
    e = random.choice(le)
    return e

def generar_d(e, phi_n):
    d = 1
    r = (d*e)%phi_n
    while r != 1:
        d = d+1
        r = (d*e)%phi_n
    return d

#fungsi code
def cifrar(mensaje, key):
    #kata-kata
    palabras = mensaje.split(" ")
    #enkripsi
    cifrado = ""
    #kata-kata terenkripsi
    palabras_cifradas = []
    for i in palabras:
        palabra = cifrar_palabra(i, key)
        palabras_cifradas.append(palabra)
    for j in palabras_cifradas:
        cifrado = cifrado + str(j) + " "
    return cifrado

#kata-kata terenkripsi
def cifrar_palabra(palabra, key):
    valores_cifrados = []
    valores = []
    n, e = key
    #enkripsi
    cifrado = ""
    for i in palabra:
        x = ord(i)
        valores.append(x)
    for j in valores:
        c = (j ** e) % n
        valores_cifrados.append(c)
    for k in valores_cifrados:
        cifrado = cifrado + str(k) + " "
    return cifrado

#decipher(menguraikan)
def descifrar(mensaje, key):
    numeros = mensaje.split("  ")
    original = ""
    #decode(membaca sandi)
    descifrado = []
    for i in numeros:
        pal = descifrar_numero(i, key)
        descifrado.append(pal)
    for j in descifrado:
        original = original + str(j) + " "
    return original

#decipher number(menguraikan nomor)
def descifrar_numero(numero, key):
    lista_numeros_descifrados = []
    lista_numeros = []
    n, d = key
    descifrado = ""
    numeros = numero.split(" ")
    for i in numeros:
        if(i != ''):
            x = int(i)
            lista_numeros.append(x)
    for j in lista_numeros:
        m = (j ** d) % n
        lista_numeros_descifrados.append(m)
    for k in lista_numeros_descifrados:
        letra = chr(k)
        descifrado = descifrado + str(letra)
    return descifrado

#generate keys(hasil kunci)
def generar_llaves():
    p = 239
    q = 103
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = generar_e(phi_n)
    d = generar_d(e, phi_n)
    return (n, e), (n, d)