import time
import random
import socket

class Client:
    def __init__(self, HOST, PORT, ID):
        self.HOST = HOST
        self.PORT = PORT
        self.ID = ID
        self.syncing = False
        return

    def sendProduction(self, production, productionType, productionTime):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))

        msgToServer = "[PROCESSO {}] {}: {} | TEMPO: {}".format(self.ID, productionType, production, productionTime)
        
        sock.sendall(str.encode(msgToServer))

        serverMsg = sock.recv(1024).decode()

        if(serverMsg == "SYNC"):
            self.syncing = True
        
        sock.sendall(str.encode("\\exit"))
        sock.close()
        
        return

    def getSyncTime(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))

        msgToServer = "[PROCESSO {}] WAITING DELTA TIME".format(self.ID)
        
        sock.sendall(str.encode(msgToServer))

        serverMsg = sock.recv(1024).decode()

        timeToSync = 0

        if(serverMsg == "OK"):
            self.syncing = False
        
        else:
            timeToSync = float(serverMsg)
        
        sock.sendall(str.encode("\\exit"))
        sock.close()

        return timeToSync



class Production:
    def __init__(self, type):
        self.localTime = time.time()
        self.production = 0
        self.productionType = type
    
    def product(self):
        self.production += 1
        self.localTime += 2

    def getProduction(self):
        return self.production

    def getProductionType(self):
        return self.productionType

    def getLocalTime(self):
        return self.localTime
    
    def showTime(self):
        t = time.localtime(self.localTime)
        rT = []

        rT.append(t[0])

        for i in range(1, 6):
            if t[i] < 10:
                rT.append("0" + str(t[i]))
            
            else:
                rT.append(t[i])
        
        formatedTime = "{}:{}:{} {}/{}/{}".format(rT[3], rT[4], rT[5], rT[2], rT[1], rT[0])
        print(formatedTime)

        return formatedTime

    def syncTime(self, timeToGo):
        self.localTime += timeToGo


def main():
    client = Client("10.103.10.103", 8081, 1)
    prod = Production("TEMPERATURA (°C)")

    while(True):

        if(client.syncing == False):
            doCycle = random.randrange(0, 2) 

            if doCycle == 1:
               
                prod.product()

                production = prod.getProduction()
                productionType = prod.getProductionType()
                productionTime = prod.getLocalTime()

                client.sendProduction(production, productionType, productionTime)
            
            
            timeToDelay = random.randrange(0, 11)
            time.sleep(timeToDelay)

        else:
            timeToGo = client.getSyncTime()
            prod.syncTime(timeToGo)


    return

if __name__ == "__main__":
    main()
