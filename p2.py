import time
import random
import socket
import threading

class Server:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.HOST, self.PORT))
        self.sock.listen(10)

        self.openLog()

        self.slavesDeltaTime = {
            "1" : -1,
            "2" : -1,
            "3" : -1,            }
        
        self.slavesLastTime = {
            "1" : -1,
            "2" : -1,
            "3" : -1
            }

        self.slavesSyncState = {
            "1" : -1,
            "2" : -1,
            "3" : -1
            }
        
        self.canChangeState = False
        self.synced = True
    
    def openLog(self):
        self.log = open("log.txt", "a", encoding='utf8')
        self.log.write("______________________||_____________________\n")
        self.log.close()
        return

    def saveSlaveTime(self, data):
        data = data.split(" ")
        index = data[1].replace("]", "")
        self.slavesLastTime[index] = float(data[-1])
        return index

    def canCalculateBerkeley(self):
        if (
        self.slavesSyncState["1"] == 1 and
        self.slavesSyncState["2"] == 1 and
        self.slavesSyncState["3"] == 1):
            self.writeToLog("\n")
            self.writeToLog("|SINCRONIZANDO PROCESSOS|")

            print("\n")
            print("|SINCRONIZANDO PROCESSOS|")
            print("\n")

            self.writeToLog("|SINCRONIZAÇÃO | TEMPO ANTERIOR|")
            print("|SINCRONIZAÇÃO | TEMPO ANTERIOR|")
            print("\n")
            p1String = "|1º PROCESSO|"
            p2String = "|2º PROCESSO|"
            p3String = "|3º PROCESSO|"

            p1String += self.getBeforeTime("1")
            p2String += self.getBeforeTime("2")
            p3String += self.getBeforeTime("3")

            self.writeToLog(p1String)
            self.writeToLog(p2String)
            self.writeToLog(p3String)
            print(p1String)
            print(p2String)
            print(p3String)

            return True
        
        else:
            return False
    
    def getBeforeTime(self, pid):
        t = time.localtime(self.slavesLastTime[pid])
        rT = []

        rT.append(t[0])

        for i in range(1, 6):
            if t[i] < 10:
                rT.append("0" + str(t[i]))
            
            else:
                rT.append(t[i])
        
        formatedTime = " |SINCRONIZAÇÃO | TEMPO ANTERIOR|: {}:{}:{} {}/{}/{}".format(rT[3], rT[4], rT[5], rT[2], rT[1], rT[0])

        return formatedTime

    def getAfterTime(self, pid):
        t = time.localtime(self.slavesLastTime[pid])
        rT = []

        rT.append(t[0])

        for i in range(1, 6):
            if t[i] < 10:
                rT.append("0" + str(t[i]))
            
            else:
                rT.append(t[i])
        
        formatedTime = " SINCRONIZAÇÃO | TEMPO DEPOIS: {}:{}:{} {}/{}/{}".format(rT[3], rT[4], rT[5], rT[2], rT[1], rT[0])

        return formatedTime
    
    def calculateBerkeley(self):
        diffP1 = self.slavesLastTime["2"] - self.slavesLastTime["1"]
        diffP3 = self.slavesLastTime["2"] - self.slavesLastTime["3"]

        mean = (0 + diffP1 + diffP3) / 3

        self.slavesDeltaTime["2"] = mean
        self.slavesDeltaTime["1"] = diffP1 + mean
        self.slavesDeltaTime["3"] = diffP3 + mean
        self.slavesLastTime["2"] += self.slavesDeltaTime["2"]
        self.slavesLastTime["1"] += self.slavesDeltaTime["1"]
        self.slavesLastTime["3"] += self.slavesDeltaTime["3"]

        self.writeToLog("SINCRONIZAÇÃO | TEMPO DEPOIS")
        print("\n")
        print("SINCRONIZAÇÃO | TEMPO DEPOIS")
        print("\n")

        p1String = "|1º PROCESSO|"
        p2String = "|2º PROCESSO|"
        p3String = "|3º PROCESSO|"

        p1String += self.getAfterTime("1")
        p2String += self.getAfterTime("2")
        p3String += self.getAfterTime("3")

        self.writeToLog(p1String)
        self.writeToLog(p2String)
        self.writeToLog(p3String)
        print(p1String)
        print(p2String)
        print(p3String)

        self.canChangeState = True

        return

    def canSendDeltaTime(self):
        if (
        self.slavesSyncState["1"] == -1 and
        self.slavesSyncState["2"] == -1 and
        self.slavesSyncState["3"] == -1):
            return False
        
        else:
            return True

    def isAllSent(self):
        if (
        (
            self.slavesSyncState["1"] == 0 and
            self.slavesSyncState["2"] == 0 and
            self.slavesSyncState["3"] == 0) or
        (
            self.slavesSyncState["1"] == -1 and
            self.slavesSyncState["2"] == -1 and
            self.slavesSyncState["3"] == -1
        )):
            self.slavesSyncState["1"] = -1
            self.slavesSyncState["2"] = -1
            self.slavesSyncState["3"] = -1
            self.canChangeState = False

            if self.synced == False:
                self.writeToLog("|SINCRONIZAÇÃO FINALIZADA|")
                self.writeToLog("\n")
                print("\n")
                print("|SINCRONIZAÇÃO FINALIZADA|")
                print("\n")
                self.synced = True

            return True
        
        else:
            return False
        
    def sendDeltaTime(self, index):
        timeToGo = self.slavesDeltaTime[index]
        if(self.canChangeState):
            self.slavesDeltaTime[index] = 0
            self.slavesSyncState[index] = 0
            return timeToGo
        else:
            return 0

    def mustSync(self, index):
        for i in self.slavesLastTime.keys():
            if i != -1:
                if self.slavesLastTime[index] % self.slavesLastTime[i] >= 1:
                    return True

    def processFormatedTime(self, pid):
        t = time.localtime(self.slavesLastTime[pid])
        rT = []

        rT.append(t[0])

        for i in range(1, 6):
            if t[i] < 10:
                rT.append("0" + str(t[i]))
            
            else:
                rT.append(t[i])
        
        formatedTime = "{}:{}:{} {}/{}/{}".format(rT[3], rT[4], rT[5], rT[2], rT[1], rT[0])

        return formatedTime

    def receiveMessage(self):
        conn, address = self.sock.accept()

        data = conn.recv(1024).decode()

        if data == "\\exit":
            conn.close()
            return
        
        if data.find("WAITING DELTA TIME") > -1:
            if(self.canCalculateBerkeley()):
                self.calculateBerkeley()
            
            if self.canSendDeltaTime():
                timeToGo = self.sendDeltaTime(data.split(" ")[1].replace("]", ""))
                conn.send(str.encode(str(timeToGo)))
                self.isAllSent()
            else:
                if(self.isAllSent()):
                    conn.send(str.encode("OK"))
                else:
                    conn.send(str.encode("0"))

        
        else:
            index = self.saveSlaveTime(data)
            timeFormated = self.processFormatedTime(index)
            data = data.replace(str(self.slavesLastTime[index]), timeFormated)
            print(data)
            self.writeToLog(data)

            if ( self.mustSync(index) ):
                conn.send(str.encode("SYNC"))
                self.slavesSyncState[index] = 1
                self.synced = False

            else:
                conn.send(str.encode("OK"))

        return
    
    def writeToLog(self, msg):
        self.log = open("log.txt", "a", encoding='utf8')
        self.log.write(msg)
        self.log.write("\n")
        self.log.close()
        return

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

        if(sock.recv(1024).decode() == "SYNC"):
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

def createResponsible():
    server = Server("10.103.10.103", 8081)
    while(True):
        server.receiveMessage()

    return

def runProduction():
    client = Client("10.103.10.103", 8081, 2)
    prod = Production("TEMPERATURA (°F)")

    while(True):
        if(client.syncing == False):
            doCycle = random.randrange(0, 2) # Probabilidade de Ciclo.

            if doCycle == 1:
                # Realiza o Ciclo.
                prod.product()

                production = prod.getProduction()
                productionType = prod.getProductionType()
                productionTime = prod.getLocalTime()

                client.sendProduction(production, productionType, productionTime)
            
            # Adormece por um período aleatório.
            timeToDelay = random.randrange(0, 11)
            time.sleep(timeToDelay)
        
        else:
            timeToGo = client.getSyncTime()
            prod.syncTime(timeToGo)
    return

def main():
    server = threading.Thread(target=createResponsible)
    server.start()
    client = threading.Thread(target=runProduction)
    client.start()
    return

if __name__ == "__main__":
    main()
