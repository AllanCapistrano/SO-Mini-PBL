import _thread
import time, random
from file import File

from string import ascii_lowercase

# Fução que gera uma palavra com caracteres aleatórios.
# @param length - int | Tamanho da palavra a ser gerada.
# @return string.
def get_random_string(length:int):
    return ''.join(random.choices(ascii_lowercase, k = length))

numFiles = 3 # Quantidade de arquivos.

file = File(numFiles) # Variável de controle.

# Classe de processos que podem ler ou escrever no arquivo.
# @ param wr - int | Identificador do processo.
def writer_reader(wr:int):
    time.sleep(random.randint(1, 5))

    while True:
        # Escolha aleatória se será feita uma escrita ou leitura.
        if(random.randint(0, 1)): # Se for Escrita
            file.downWrite() # Obtém acesso ao arquivo.
            
            content_to_write = get_random_string(random.randint(1, 5))# Gera o conteúdo a escrito.
            print(f"\nProcesso {wr} - Escrevendo: '{content_to_write}'")
            file.write_line(content_to_write) # Realiza a escrita no arquivo.
            time.sleep(random.randint(1, 5))
            file.upWrite() # Libera o acesso ao arquivo.
            
            print(f"Processo {wr} - parou de escrever.\n")
        else:
            file.downRead() # Obtém acesso ao arquivo.
            
            print(f"Processo {wr} - lendo...")
            file.read() # Realiza a leitura do arquivo.
            time.sleep(random.randint(1, 5))
           
            file.upRead() # Libera o acesso ao arquivo.
            
            print(f"Processo {wr} - parou de ler.\n")

# Processo sincronizador.
# @param s - int | Identificador do processo.
# @param numFiles - int | Número de arquivos.
def syncronizer(s:int, numFiles:int):
    numFiles = numFiles
    
    while True:
        time.sleep(random.randint(1, 3))
        file.downSync() # Obtém acesso ao arquivo.

        print(f"\nSincronizador {s} iniciando sincronização...")
        time.sleep(random.randint(1, 3))

        file.sync() # Realiza a sincronização dos arquivos.
        file.upSync() # Libera o acesso ao arquivo.

        print(f"Sincronizador {s} terminou a sincronização.\n")



# Cria o processo que irá sincronizar os arquivos.
_thread.start_new_thread(syncronizer, tuple([0,numFiles]))


# Cria os processos que podem ler ou escrever no arquivo.
for i in range(8):
    _thread.start_new_thread(writer_reader, tuple([i]))


while 1: pass