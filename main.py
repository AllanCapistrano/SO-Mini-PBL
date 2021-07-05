import _thread
import time, random
from file import File

from string import ascii_lowercase
from random import choices

# Fução que gera uma palavra com caracteres aleatórios.
# @param length - int | Tamanho da palavra a ser gerada.
# @return string.
def get_random_string(length:int):
    return ''.join(choices(ascii_lowercase, k = length))

numFiles = 3 # Quantidade de arquivos.

file = File(numFiles) # Variável de controle.

# Processo escritor.
# @param e - int | Identificador.
def writer(e:int):
    while True:
        time.sleep(random.randint(1, 5))
        file.acquireWriteLock() # Obtém acesso ao arquivo.
        
        print(f"\nEscritor {e} pensando nos dados...\n",end='')
        time.sleep(random.randint(1, 5))
        
        content_to_write = get_random_string(random.randint(1, 5))# Gera o conteúdo a escrito.
        file.write_line(content_to_write) # Realiza a escrita no arquivo.
        
        time.sleep(random.randint(1, 5))
        file.releaseWriteLock() # Libera o acesso ao arquivo.
        
        print(f"Escritor {e} - parou de escrever.\n")

# Processo escritor.
# @param l - int | Identificador.
def reader(l:int):
    while True:
        time.sleep(random.randint(1, 10))
        file.acquireReadLock() # Obtém acesso ao arquivo.
        
        print(f"Leitor {l} - lendo...")
        time.sleep(random.randint(1, 5))
        
        file.read() # Realiza a leitura do arquivo.
        file.releaseReadLock() # Libera o acesso ao arquivo.
        
        print(f"Leitor {l} - parou de ler.\n")

# Processo sincronizador.
# @param s - int | Identificador.
# @param numFiles - int | Número de arquivos.
def syncronizer(s:int, numFiles:int):
    numFiles = numFiles
    
    while True:
        time.sleep(random.randint(1, 3))
        file.acquireSyncLock() # Obtém acesso ao arquivo.

        print(f"\nSincronizador {s} iniciando sincronização...")
        time.sleep(random.randint(1, 3))

        file.sync() # Realiza a sincronização dos arquivos.
        file.releaseSyncLock() # Libera o acesso ao arquivo.

        print(f"Sincronizador {s} terminou a sincronização.\n")

# Cria os processos que irão realizar a escrita no arquivo
for i in range(2):
    _thread.start_new_thread(writer, tuple([i]))

# Cria o processo que irá sincronizar os arquivos
_thread.start_new_thread(syncronizer, tuple([0,numFiles]))

# Cria os processos que irão realizar a leitura do arquivo
for i in range(3):
    _thread.start_new_thread(reader, tuple([i]))


while 1: pass