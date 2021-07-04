import threading

class File:
    readersCount = 0 # Quantidade de leitores no momento
    mutex = threading.Semaphore(1) # Semáforo mutex para alteração da quantidade de leitores
    file = threading.Semaphore(1) # Semáforo para acesso ao arquivo

    fileSync = threading.Semaphore(1) # Semáforo para sincronização do arquivo

    # Função para bloquear o acesso ao arquivo por parte dos leitores
    def acquireReadLock(self):
        # Tenta obter permissão para a leitura do arquivo
        if(self.fileSync.acquire()):
            global readersCount
            
            # Tenta obter acesso a variável readersCount
            self.mutex.acquire()
            self.readersCount += 1

            # Somente se for o primeiro leitor bloqueia o acesso ao arquivo. 
            if(self.readersCount == 1):
                self.file.acquire()

            # Libera o acesso a variável readersCount
            self.mutex.release()

            # Libera o acesso ao arquivo.
            self.fileSync.release()

    # Função para liberar o acesso ao arquivo por parte dos leitores
    def releaseReadLock(self):
        global readersCount
        
        # Tenta obter acesso a variável readersCount
        self.mutex.acquire()
        self.readersCount -= 1

        # Somente se for o último leitor libera o acesso ao arquivo. 
        if(self.readersCount == 0):
            self.file.release()

        # Libera o acesso a variável readersCount
        self.mutex.release()

    # Função para bloquear o acesso ao arquivo por parte dos escritores
    def acquireWriteLock(self):
        # Tenta bloquear o acesso dos leitores ao arquivo
        self.fileSync.acquire()
        
        # Tenta obter acesso ao arquivo para realizar a escritores
        self.file.acquire()

    # Função para liberar o acesso ao arquivo por parte dos escritores
    def releaseWriteLock(self):
        # Libera o acesso ao arquivo
        self.file.release()

    # Função para bloquear o acesso ao arquivo para realizar a sincronização
    def acquireSyncLock(self):
        # Tenta obter acesso ao arquivo para realizar a sincronização
        self.file.acquire()

    # Função para liberar o acesso ao arquivo após a sincronização
    def releaseSyncLock(self):
        # Libera o acesso ao arquivo
        self.file.release()

        # Libera o acesso dos leitores ao arquivo
        self.fileSync.release()
