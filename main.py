import _thread
import time, random
from file import File

from string import ascii_lowercase
from random import choices
def get_random_string(tamanho:int):
    return ''.join(choices(ascii_lowercase, k=tamanho))

qtdArq = 3

file = File(qtdArq)

def writer(e):
    while True:

        time.sleep(random.randint(1, 5))
        file.acquireWriteLock()
        
        print(f"Escritor {e} pensando nos dados...",end='')
        time.sleep(random.randint(1, 5))
        content_to_write = get_random_string(random.randint(1, 5))
        print(f' Escrevendo "{content_to_write}"')
        
        print(f"Escritor {e} - escrevendo...")
        file.write_line(content_to_write)
        time.sleep(random.randint(1, 5))
        file.releaseWriteLock()
        
        print(f"Escritor {e} - parou de escrever.")

def reader(l):
    while True:
        time.sleep(random.randint(1, 10))
        file.acquireReadLock()
        
        print(f"Leitor {l} - lendo...")
        time.sleep(random.randint(1, 5))
        file.read()
        file.releaseReadLock()
        
        print(f"Leitor {l} - parou de ler.")

def syncronizer(s, qtdArq):
    qtdArq = qtdArq
    while True:
        time.sleep(random.randint(1, 3))
        file.acquireSyncLock()

        print(f"Sincronizador {s} iniciando sincronização...")
        time.sleep(random.randint(1, 3))

        file.sync()
        # while(qtdArq > 0):
        #     print("Sincronizando arquivo {}...".format(qtdArq))
        #     qtdArq -= 1
        #     # time.sleep(2)

        file.releaseSyncLock()

        print(f"Sincronizador {s} terminou a sincronização...")

# Cria os processos que irão realizar a escrita no arquivo
for i in range(2):
    _thread.start_new_thread(writer, tuple([i]))

# Cria o processo que irá sincronizar os arquivos
_thread.start_new_thread(syncronizer, tuple([0,qtdArq]))

# Cria os processos que irão realizar a leitura do arquivo
for i in range(3):
    _thread.start_new_thread(reader, tuple([i]))


while 1: pass