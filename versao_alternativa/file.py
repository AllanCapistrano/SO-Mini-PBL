from threading import Semaphore
import random

class File:

    readersCount = 0 # Quantidade de leitores no momento
    readersCountMutex = Semaphore(1) # Semáforo mutex para alteração da quantidade de leitores
    fileMutex = Semaphore(1) # Semáforo para acesso ao arquivo

    read_write_mutex = Semaphore(1) # Semáfaro para acesso do vetor de arquivos disponiveis para ultilização e variavel que indica se leitura esta disponivel
    available_vet = [] # vetor de booleanos que indicam se o arquivo pode ser usado ou nao

    fileSyncMutex = Semaphore(1) # Semáforo para sincronização do arquivo

    # função de construção do objeto
    # @param qtdArq, type:int, indica a quantidade de arquivos que serão usados
    # @param file_path, vetor contendo o caminho dos arquivos que serao usados, caso o vetor nao cotenha caminho de todos os arquivos os que faltarem serao criddos no diretorio /files/. Tem um valor default de None ( assim caso nao seja passado vira com esse valor )
    def __init__(self,qtdArq:int,file_path=None):
        self.qtdArq = qtdArq #salvamos a quantidade de arquivos
        if(file_path != None): # caso file_path senha sido passado ele nao tera o valor default de None
            self.file_path = file_path # salvamos o que foi passado
            #conferimos se em file_path tem todos os arquivos que serao usados ( se len(file_path) < qtrArq )
            conf = [False for _ in range(self.qtdArq)]
            for n,_ in enumerate(self.file_path):
                try:
                    conf[n]=True
                except:# so entrara na exceção se for passado mais caminhos do que arquivos declarados, entao esses paths tao salvos mas nao serao usados
                    pass
            # Caso nao tenhamos todos os que faltam sao criados no diretorio /files/
            for n,alredy_exist in enumerate(conf):
                if(not alredy_exist):
                    self.file_path.append(f'files/file_v2_{n}.txt')
        else: # caso contrario criamos os arquivos no diretorio files/
            self.file_path = [f'files/file_v2_{n}.txt' for n in range(self.qtdArq)]
        for a in range(self.qtdArq):
            try:
                open(self.file_path[a],'a')
            except:
                open(self.file_path[a],'w')
            self.available_vet.append(True)
#        for a in range(self.qtdArq):
#            print(a,"  ",self.file_path[a],'   ',self.available_vet[a])
            
    # Esta função recebe o que vai ser escrito como parametro e é responsavel por repassar para um arquivo
    def write_line(self,write_this:str):
        self.read_write_mutex.acquire() # travando edição de variaveis
        chosen_file = self.__chose_file__() # chama função que procura um arquivo para ser escrito, nota: nessa função nao preisamos bloquear o acesso pois nela nao sera feita escrita so leitura e nesta ja estamos bloqueando, entao garantimos que nenhum outro ira modifica as variaveis 
        if(chosen_file["found"]): # se achar um arquivo
            print(f"writing '{write_this}' on {chosen_file['file']}")
            with open(chosen_file['file'],'a') as file: # abrimos ele como apend
                file.write(write_this+'\n') # escrevemos o que foi passado
                file.close() # e fechamos o arquivo
            for n in range(self.qtdArq):# para cada arquivo do sistema
                self.available_vet[n] = self.file_path[n] == chosen_file['file'] # marcamos ele como nao atualizado se nao foi o arquivo que editamos
        self.read_write_mutex.release() # liberamos as variaveis
    
    # Esta função retorna o conteudo de um arquivo ja sincronizado
    def read(self):
        self.read_write_mutex.acquire()#travamos a edição das variaveis
        content = None #marcamos o conteudo da leitura como inexistente
        chosen_file = self.__chose_file__() #se for possivel pedimos um arquivo
        if(chosen_file['found']): # se houver um arquivo
            print(f'Reading content from "{chosen_file["file"]}"')
            with open(chosen_file['file'],'r') as file: # abrimos ele para leitura
                content = file.readlines()# salvamos o conteudo dele
                file.close() # e fechamos o arquivo
            print(f"content:")
            print(content)
            print(f'end of content')
        self.read_write_mutex.release()# por fim liberamos as variaveis
        return content # e retornamos os conteudo
    
    # Esta função retorna um arquivo aleatorio sincronizado
    def __chose_file__(self):
        dic = {"found" : False} #marcamos o arquivo como nao encontrado
        available_files = [] # criamos um vetor de arquivos que estao disponiveis para serem usados ( tem o conteudo mais recente)
        for n in range(self.qtdArq):# para cada arquivo do sistema
            # print(self.available_vet)
            # print(self.file_path[n])
            if(self.available_vet[n]):# se ele estiver atualizado
                available_files.append(self.file_path[n]) # adicionamos ele no vetor
        try:# entao tentamos escolher 1 arquivo aleatorio dos presentes no dicionario
            dic['file'] = random.choices(available_files)[0]
            dic['found']=True # caso consigamos escolher 1 entao marcamos como arquivo achado
        except:# caso tenhamos algum erro é porque nao existem arquivos marcados como atualizados entao o dicionario ainda nao foi atualizado e marca arquivo nao encontrado
            pass #portanto nada precisa ser feito ( por este metodo)
        #print(dic) # printamos o que sera retornado para debug
        return dic # por fim retornamos o dicionario contento se o arquivo foi achado e caso tenha sido o path do arquivo

    #Função que sincroniza o conteudo dos arquivos    
    def sync(self):
        print(f'Attempting to syncing content of files')
        self.read_write_mutex.acquire() #trava leitura e escrita
        updated_files = [] #lista de arquivos atualizados
        to_be_updated_files = [] #lista de arquivos nao atualziados
        for n,a in enumerate(self.available_vet): #para cada arquivo do sistema
            if(a): # se estiver atualziado adicionamos na lista de atualziados
               updated_files.append(self.file_path[n])
            else:# se nao atualizamos na lista de nao atualizados
                to_be_updated_files.append(n)
        print(f"File with content updated: ", end='')
        for f in updated_files:# 
            print(f,end=", ")
        print()
        if(len(updated_files) <1):# se nao houver arquivo da lista de atualizados gera um erro
            raise Exception("There was a problem - no file is considered as contain the most recent version")
        conteudo = None#cria vatiavel com conteudo que sera atualizado nos outros arquivos como None para ser sobreescria
        with open(updated_files[0],'r') as file:# salva o conteudo do primeiro arquivo atualizado
            conteudo = file.readlines()
            file.close()
        if(conteudo == None):# se ainda estiver com None algum erro aconteceu na leitura do arquivo entao gera um erro
            raise Exception(f"Not able to open {updated_files[0]}")
        # print("Linhas do arquivo mais atualizado:")
        # print(conteudo)
        print("Updating content on: ",end='')
        for a in to_be_updated_files:# para cara arquivo que sera atualizado
            print(self.file_path[a],end=', ')
            old_content = None
            with open(self.file_path[a],'r') as file_to_update:# salva o antigo conteudo do arquivo para comparação
                old_content = file_to_update.readlines()
                file_to_update.close()
            with open(self.file_path[a],'a') as file_to_update:#e so fazemos a escrita do conteudo que falta. essa comparação é feita pela contagem de linhas
                # print("linhas lidas do arquivo:",self.file_path[a])
                # print(old_content)
                # print("linhas que serão adicionadas:", end='')
                for l in conteudo[len(old_content):]:
                    #print(l,end=", ")
                    file_to_update.write(l)
                #print()
            self.available_vet[a] = True # marca esse arquivo como atualizado
        print()
        print("Content of files: ",end="")
        for a in range(self.qtdArq):
            print(f'"{self.file_path[a]}" is {"the latest" if self.available_vet[a] else "not the latest"}',end=', ')
        print()
        self.read_write_mutex.release()
        return

    #metodo que printa o conteudo do objeto ( quando chamamos print() e passamos um objeto sera chamado a função __str__ do obj, entoa essa função diz como o objeto deve ser printado, retornando uma string que sera printada)
    def __str__(self):
        return f"Num of files: {self.qtdArq}\n"+ f'Files: {self.file_path}\n'+ f"available vet: {self.available_vet}"

    # Função para bloquear o acesso ao arquivo por parte dos leitores
    def acquireReadLock(self):
        # Tenta obter permissão para a leitura do arquivo
        if(self.fileSyncMutex.acquire()):
            # Tenta obter acesso a variável readersCount
            self.readersCountMutex.acquire()
            self.readersCount += 1

            # Somente se for o primeiro leitor bloqueia o acesso ao arquivo. 
            if(self.readersCount == 1):
                self.fileMutex.acquire()

            # Libera o acesso a variável readersCount
            self.readersCountMutex.release()

            # Libera o acesso ao arquivo.
            self.fileSyncMutex.release()

    # Liber
    def releaseReadLock(self):
        # Tenta obter acesso a variável readersCount
        self.readersCountMutex.acquire()
        self.readersCount -= 1

        # Somente se for o último leitor libera o acesso ao arquivo. 
        if(self.readersCount == 0):
            self.fileMutex.release()

        # Libera o acesso a variável readersCount
        self.readersCountMutex.release()

    def acquireWriteLock(self):
        # Tenta bloquear o acesso dos leitores ao arquivo
        self.fileSyncMutex.acquire()
        
        # Tenta obter acesso ao arquivo para realizar a escrita
        self.fileMutex.acquire()

    def releaseWriteLock(self):
        # Libera o acesso ao arquivo
        self.fileMutex.release()

    def acquireSyncLock(self):
        # Tenta obter acesso ao arquivo para realizar a sincronização
        self.fileMutex.acquire()
        
    def releaseSyncLock(self):
        # Libera o acesso ao arquivo
        self.fileMutex.release()

        # Libera o acesso dos leitores ao arquivo
        self.fileSyncMutex.release()
