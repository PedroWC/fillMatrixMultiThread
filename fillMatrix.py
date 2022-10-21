import threading as T
from time import time
from random import randint as rand

def printMatrizQuadrada(matriz):
    cont = len(matriz[0])
    for i in range(cont):
        for j in range(cont):
            print(str(matriz[i][j]), end=' ')
        print()

def criaMatriz(n):
    matriz = []
    for i in range(n):
        matriz.append([-1]*n)

    return matriz


class Serial:

    def __init__(self, n: int):

        self.n      = n
        self.matriz = criaMatriz(n)


    def main(self) -> float:
        
        timein = time()

        for j in range(self.n):
            for i in range(self.n):
                self.matriz[i][j] = rand(0, 9) if (j == 0) else self.matriz[rand(0, 9) % self.n][rand(0, 9) % j]
        
        timeout = time()
        
        return (timeout - timein)
       
class Paralela_N_Threads:
    def __init__(self, n: int):
        self.n          = n
        self.bar1       = T.Barrier(self.n)
        self.bar2       = T.Barrier(self.n+1)
        self.matriz     = criaMatriz(n)
        self.threadsId  = []

        for linha in range(self.n):
            self.threadsId.append(T.Thread(target=self.f, args=[linha]))
        

    def main(self) -> float:

        timein = time()

        for linha in range(self.n):
            self.threadsId[linha].start()
        
        self.bar2.wait()

        timeout = time()
        
        return (timeout - timein)
    
    def f(self, linha):

        for j in range(self.n):
            self.matriz[linha][j] = rand(0, 9) if(j == 0) else self.matriz[rand(0, 9) % self.n][rand(0, 9) % j]
        
            self.bar1.wait()

        self.bar2.wait()

class Paralela_NxN_Threads:

    def __init__(self, n: int):
        self.n          = n
        self.fim        = T.Barrier(self.n+1)
        self.inicio     = T.Barrier(self.n**2)
        self.matriz     = criaMatriz(n)
        self.semaforo   = T.Semaphore(self.n**2)
        self.threadsId  = []

        for i in range(self.n):
            linhaThreadAtual = []
            for j in range(self.n):
                linhaThreadAtual.append(T.Thread(target=self.f, args=[i, j]))
            self.threadsId.append(linhaThreadAtual)


    def main(self) -> float:

        timein = time()

        for i in range(self.n):
            for j in range(self.n):
                self.threadsId[i][j].start()

        self.fim.wait()

        timeout = time()
        return (timeout - timein)

    def f(self, i, j):

        # barreira "inicio" espera todas as threads iniciarem
        # para que nenhum join espere uma thread nao iniciada
        self.inicio.wait()

        if(j == 0):
            self.matriz[i][j] = rand(0, 9)
        else:
            linha = rand(0, 9) % self.n
            coluna = rand(0, 9) % j
            # join espera a "thread que preenche matriz[linha][coluna]" terminar
            self.threadsId[linha][coluna].join()
            # metodo acquire = down
            self.semaforo.acquire()
            self.matriz[i][j] = self.matriz[linha][coluna]

        # metodo release = up
        self.semaforo.release(self.n**2)
        
        if(j == self.n - 1):
            self.fim.wait()

# testes

for n in range(1, 100, 10):

    metodo1 = Serial(n)
    metodo2 = Paralela_N_Threads(n)
    metodo3 = Paralela_NxN_Threads(n)

    print("Tempo de execução para matriz quadrada ({0}x{1}) e estratégia sequencial é:               {2:.10f} segundos.".format(n, n, metodo1.main()))
    print("Tempo de execução para matriz quadrada ({0}x{1}) e estratégia paralela com n threads é:   {2:.10f} segundos.".format(n, n, metodo2.main()))
    print("Tempo de execução para matriz quadrada ({0}x{1}) e estratégia paralela com n*n threads é: {2:.10f} segundos.".format(n, n, metodo3.main()))

    print()
