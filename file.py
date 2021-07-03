import threading

class File:
    readersCount = 0 # Quantidade de leitores no momento
    mutex = threading.Semaphore(1) # Semáforo mutex para alteração da quantidade de leitores
    file = threading.Semaphore(1) # Semáforo para acesso ao arquivo

    fileSync = threading.Semaphore(1) # Semáforo para sincronização do arquivo

    # Função para bloquear o acesso ao arquivo por parte dos leitores
    def acquireReadLock(self):
        # Tenta obter permissão para a leitura do arquivo
        self.fileSync.acquire()
        
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

    # Liber
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

    def acquireWriteLock(self):
        # Tenta bloquear o acesso dos leitores ao arquivo
        self.fileSync.acquire()
        
        # Tenta obter acesso ao arquivo para realizar a escrita
        self.file.acquire()

    def releaseWriteLock(self):
        # Libera o acesso ao arquivo
        self.file.release()

    def acquireSyncLock(self):
        # Tenta obter acesso ao arquivo para realizar a sincronização
        self.file.acquire()
        
    def releaseSyncLock(self):
        # Libera o acesso ao arquivo
        self.file.release()

        # Libera o acesso dos leitores ao arquivo
        self.fileSync.release()
