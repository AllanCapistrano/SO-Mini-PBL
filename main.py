import _thread
import time, random
from file import File

file = File()

def writer(e):
    while True:

        time.sleep(random.randint(1, 5))
        file.acquireWriteLock()
        
        print("Escritor {} pensando nos dados...".format(e))
        time.sleep(random.randint(1, 5))
        
        print("Escritor {} - escrevendo...".format(e))
        time.sleep(random.randint(1, 5))
        file.releaseWriteLock()
        
        print("Escritor {} - parou de escrever.".format(e))

def reader(l):
    while True:
        time.sleep(random.randint(1, 10))
        file.acquireReadLock()
        
        print("Leitor {} - lendo...".format(l))
        time.sleep(random.randint(1, 5))
        file.releaseReadLock()
        
        print("Leitor {} - parou de ler.".format(l))

def syncronizer(s):
    
    while True:
        qtdArq = 3
        
        time.sleep(random.randint(1, 3))
        file.acquireSyncLock()

        print("Sincronizador {} iniciando sincronização...".format(s))
        time.sleep(random.randint(1, 3))

        while(qtdArq > 0):
            print("Sincronizando arquivo {}...".format(qtdArq))
            qtdArq -= 1
            # time.sleep(2)

        file.releaseSyncLock()

        print("Sincronizador {} terminou a sincronização...".format(s))

# Cria os processos que irão realizar a escrita no arquivo
for i in range(2):
    _thread.start_new_thread(writer, tuple([i]))

# Cria o processo que irá sincronizar os arquivos
_thread.start_new_thread(syncronizer, tuple([0]))

# Cria os processos que irão realizar a leitura do arquivo
for i in range(3):
    _thread.start_new_thread(reader, tuple([i]))


while 1: pass