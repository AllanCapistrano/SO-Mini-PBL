import os
from threading import Semaphore
import random

class File:
    # Quantidade de leitores no momento
    readersCount = 0
    # Semáforo mutex para alteração da quantidade de leitores
    readersCountSemaphore = Semaphore(1)
    # Semáforo mutex para acesso ao arquivo
    fileSemaphore = Semaphore(1)

    # Semáfaro mutex para acesso do vetor de arquivos disponiveis para 
    # ultilização e variavel que indica se leitura esta disponivel
    read_write_semaphore = Semaphore(1)
    # vetor de booleanos que indicam se o arquivo pode ser usado ou nao
    available_vet = []
    # Flag para indica se os arquivos podem ser lidos
    can_be_read = True

    readersSemaphore = Semaphore(1) # Semáforo para sincronização do arquivo

    # Função de inicialização.
    #
    # @param qtdArq - int | Indica a quantidade de arquivos que serão usados
    # @param file_path - Array | Vetor contendo o caminho dos arquivos que serão 
    # usados, caso o vetor não cotenha caminho de todos os arquivos os que 
    # faltarem serão criados no diretório files/.
    def __init__(self, qtdArq:int, file_path = None):
        # Caso não exista o diretório files/ o mesmo é criado.
        if(not os.path.isdir(os.getcwd()+"/files/")):
            os.makedirs(os.getcwd()+"/files/")
        
        self.qtdArq = qtdArq # Salvando a quantidade de arquivos.
        
        if(file_path != None): # Caso seja passado algum file_path.
            self.file_path = file_path
            # Conferindo se em file_path tem todos os arquivos que serão usados ( se len(file_path) < qtrArq )
            conf = [False for _ in range(self.qtdArq)]
            
            for n,_ in enumerate(self.file_path):
                try:
                    conf[n]=True
                except: # Só entrara na exceção se for passado mais caminhos do que arquivos declarados, entao esses paths tao salvos mas nao serao usados
                    pass
            
            # Caso não existam todos os arquivos, são criados no diretorio files/
            for n,alredy_exist in enumerate(conf):
                if(not alredy_exist):
                    self.file_path.append(f'files/file{n}.txt')
        else: # Caso contrário os arquivos são criados no diretorio files/
            self.file_path = [f'files/file{n}.txt' for n in range(self.qtdArq)]
        
        # -- Verificando se os arquivos estão sincronizados --
        
        num_lines = [] # Armazenar a quantidade de linhas dos arquivos.
        
        for a in range(self.qtdArq):
            try:
                f = open(self.file_path[a],'r')
                num_lines.append(len(f.readlines())) # Salvando a quantidade de linha do arquivo
            except: # Caso o arquivo não exista.
                open(self.file_path[a],'w') # Criando o arquivo.
                num_lines.append(0) # Número de linhas é zero.
            
            self.available_vet.append(True)
        
        with_more_lines = 0
        poss_file_with_more_lines=None
        with_less_lines=0
        
        for a in range(self.qtdArq):
            # Caso o arquivo possua a maior quantidade de linhas, sua posição é salvada
            if(num_lines[a] > with_more_lines):# se ele tiver a maior quantidade de linhas salvamos a sua posição
                with_more_lines = num_lines[a]
                poss_file_with_more_lines = a
            
            if(num_lines[a] < with_less_lines):
                with_less_lines = num_lines[a]
        
        # Caso o arquivo com mais linhas, não seja o mesmo com menos linhas,
        # é necessário acontecer uma sincronização.
        if(with_more_lines != with_less_lines):
            print("Sincronizando arquivos...")
            
            content = None
            
            # O conteúdo do arquivo com mais linhas é salvado.
            with open(self.file_path[poss_file_with_more_lines],'r') as file:
                content = file.readlines()
                file.close()
                
            # Para os demais arquivos, é salvado o conteúdo do arquivo mais atual.
            for a in range(self.qtdArq):
                with open(self.file_path[a],'a') as file:
                    for l in content[num_lines[a]:]:
                        file.write(l)
                    file.close()
    
    # Função para escrever em um arquivo.
    #
    # @param write_this - string | O que será escrito no arquivo.
    def write_line(self, write_this:str):
        self.read_write_semaphore.acquire() # Bloqueando o acesso a variável can_be_read.
        self.can_be_read = False # Marcando arquivos como nao podendo mais ser lidos
        
        # Chamando a função que retorna aleatoriamente um arquivo para ser escrito.
        chosen_file = self.__chose_file__()
        
        if(chosen_file["found"]):
            print(f"Escrevendo '{write_this}' em {chosen_file['file']}")
            
            # Escreve no arquivo o que foi passado.
            with open(chosen_file['file'],'a') as file: 
                file.write(write_this+'\n')
                file.close()
            
            # Marca os demais arquivos como não atualizado.
            for n in range(self.qtdArq):
                self.available_vet[n] = self.file_path[n] == chosen_file['file'] 
        
        self.read_write_semaphore.release() # Libera o acesso a variável can_be_read.
    
    # Função para realizar a leitura do arquivo.
    #
    # @return string | Conteúdo do arquivo.
    def read(self):
        self.read_write_semaphore.acquire() # Bloquea o acesso a variável can_be_read.
        
        content = None # Inicializando a variável conteúdo.
        
        # Verifica se pode realizar a leitura.
        if(self.can_be_read):
            chosen_file = self.__chose_file__() # Escolhe um arquivo aleatoriamente
            
            if(chosen_file['found']):
                print(f'Lendo o conteúdo de "{chosen_file["file"]}"')
                
                with open(chosen_file['file'],'r') as file:
                    content = file.readlines()
                    file.close()
                
                print(f"Conteúdo:")
                print(content)
        else:
            print("Não é permitida a leitura do arquivo, é necessário uma sincronização.")
        
        self.read_write_semaphore.release() # Libera o acesso a variável can_be_read.
        
        return content
    
    # Função que escolhe aleatoriamente um arquivo.
    #
    # @return - {} | Dicionário com as informações do arquivo.
    def __chose_file__(self):
        dic = {"found" : False} # Inicializando o dicionário.
        available_files = [] # Array com os arquivos mais atuais.
        
        for n in range(self.qtdArq):
            # Se o arquivo estiver atualizado
            if(self.available_vet[n]):
                available_files.append(self.file_path[n])
        
        try:
            dic['file'] = random.choices(available_files)[0]
            dic['found'] = True
        except: # Caso não consiga escolher um arquivo, indica que não existe nenhum arquivo atualizado.
            pass
        
        return dic

    # Função para sincronizar os arquivos 
    def sync(self):
        print(f'Tentando sincronizar o conteúdo dos arquivos')
        
        self.read_write_semaphore.acquire() # Bloqueando a leitura/escrita dos arquivos.
        
        updated_files = [] # Lista dos arquivos atualizados.
        to_be_updated_files = [] # Lista dos arquivos desatualizados.
        
        for n,a in enumerate(self.available_vet):
            if(a):
               updated_files.append(self.file_path[n])
            else:
                to_be_updated_files.append(n)
        
        print(f"Arquivo com o conteúdo atualizado: ", end='')
        
        for f in updated_files:
            print(f,end=", ")
        
        print()
        
        # Se a lista de arquivos atualizados for menor que 1 ocorreu um erro.
        if(len(updated_files) < 1):
            raise Exception("There was a problem - no file is considered as contain the most recent version")
        
        content = None # Conteúdo para ser atualizado nos arquivos
        
        # Lendo o conteúdo do primeiro arquivo mais atualizado.
        with open(updated_files[0],'r') as file:
            content = file.readlines()
            file.close()
        
        # Caso o conteúdo for None, ocorreu um erro durante a leitura do arquivo.
        if(content == None): 
            raise Exception(f"Não foi possível abrir o arquivo {updated_files[0]}")
        
        print("Atualizando o conteúdo de: ",end='')
        
        for a in to_be_updated_files:
            print(self.file_path[a],end=', ')
            
            old_content = None
            
            # Salvando o conteúdo antigo.
            with open(self.file_path[a],'r') as file_to_update:
                old_content = file_to_update.readlines()
                file_to_update.close()
            
            # Adicionando o conteúdo mais atualizado que falta.
            with open(self.file_path[a],'a') as file_to_update:
                for l in content[len(old_content):]:
                    file_to_update.write(l)

            self.available_vet[a] = True # Definie o arquivo como atualizado.
        
        print()
        
        self.can_be_read = True # Define que todos os arquivos já podem ser lidos.
        
        print("Conteúdo dos arquivos: ",end="")
        
        for a in range(self.qtdArq):
            print(f'"{self.file_path[a]}" {"é o mais recente" if self.available_vet[a] else "não é o mais recente"}',end=', ')
        
        print()
        
        self.read_write_semaphore.release() # Liberando a leitura/escrita dos arquivos

    # Método que exibe o conteúdo do objeto (quando print() é chamado e é passado
    # um objeto, será chamado a função __str__ do objeto, então essa função diz como 
    # o objeto deve ser exibido, retornando a string que será exibida).
    def __str__(self):
        return f"Num of files: {self.qtdArq}\n"+ f'Files: {self.file_path}\n'+ f"available vet: {self.available_vet}"

    # Função para bloquear o acesso ao arquivo por parte dos leitores
    def downRead(self):
        # Tenta obter permissão para a leitura do arquivo
        if(self.readersSemaphore.acquire()):
            global readersCount
            
            # Tenta obter acesso a variável readersCount
            self.readersCountSemaphore.acquire()
            self.readersCount += 1

            # Somente se for o primeiro leitor bloqueia o acesso ao arquivo. 
            if(self.readersCount == 1):
                self.fileSemaphore.acquire()

            # Libera o acesso a variável readersCount
            self.readersCountSemaphore.release()

            # Libera o acesso ao arquivo.
            self.readersSemaphore.release()

    # Função para liberar o acesso ao arquivo por parte dos leitores
    def upRead(self):
        global readersCount
        
        # Tenta obter acesso a variável readersCount
        self.readersCountSemaphore.acquire()
        self.readersCount -= 1

        # Somente se for o último leitor libera o acesso ao arquivo. 
        if(self.readersCount == 0):
            self.fileSemaphore.release()

        # Libera o acesso a variável readersCount
        self.readersCountSemaphore.release()

    # Função para bloquear o acesso ao arquivo por parte dos escritores
    def downWrite(self):
        # Tenta bloquear o acesso dos leitores ao arquivo
        self.readersSemaphore.acquire()
        
        # Tenta obter acesso ao arquivo para realizar a escritores
        self.fileSemaphore.acquire()

    # Função para liberar o acesso ao arquivo por parte dos escritores
    def upWrite(self):
        # Libera o acesso ao arquivo
        self.fileSemaphore.release()

    # Função para bloquear o acesso ao arquivo para realizar a sincronização
    def downSync(self):
        # Tenta obter acesso ao arquivo para realizar a sincronização
        self.fileSemaphore.acquire()
         
    # Função para liberar o acesso ao arquivo por parte dos escritores
    def upSync(self):
        # Libera o acesso ao arquivo
        self.fileSemaphore.release()

        # Libera o acesso dos leitores ao arquivo
        self.readersSemaphore.release()
