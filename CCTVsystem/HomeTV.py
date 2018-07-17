# -*- coding: utf-8 -*-
import time
import ssl
import cv2
import socket
import threading
from threading import Thread
import numpy
import logging


class ImageTransmission():
    logging.basicConfig(level=logging.ERROR)

    def recvall(self,sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf:
                logging.debug("recvall() failed , newbuf hasn't value")
                return None
            buf += newbuf
            count -= len(newbuf)
        logging.debug("recvall() completed ")
        return buf


    def stringImageToFrame(self,stringData):
        try:
            data = numpy.fromstring(stringData, dtype='uint8')
            decimg = cv2.imdecode(data, 1)
            logging.debug("stringImageToFrame() completed ")
        except Exception as msg:
            logging.ERROR("stringImageToFrame() failed Check your param, Errmsg: "+msg)
            return None
        return decimg

    def frameToStringImage(self,frame):
        try:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
            data = numpy.array(imgencode)
            stringData = data.tostring()
            logging.debug("frameToStringImage() completed ")
        except Exception as msg:
            logging.ERROR("frameToStringImage() failed Check your param(have to put value of cv2), Errmsg: "+msg)
        return stringData

    def recvStringImage(self,sock,errReturn):
        length = self.recvall(sock, 32)
        if not length:
            logging.info("The server did not receive the size of the picture.")
            return errReturn
        stringData = self.recvall(sock, int(length))
        if not stringData:
            logging.info("The server did not receive the picture.")
            return errReturn
        data = numpy.fromstring(stringData, dtype='uint8')
        logging.debug("recvStringImage() completed ")
        return data

    def sendStringImage(self,sock,stringData):
        sock.send(str(len(stringData)).ljust(32))
        sock.send(stringData)
        logging.debug("sendStringImage() completed ")


class SimTV():

    def __init__(self,ip,port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.sender = ImageTransmission()
        self.sock = socket.socket()

        self.sock = ssl.wrap_socket(self.sock,
                                   ca_certs="cipher/server.crt",
                                   cert_reqs=ssl.CERT_REQUIRED)

        self.sock.connect((self.TCP_IP, self.TCP_PORT))

        self.noiseImage = cv2.imread("rsc/default.png")
        self.noiseImage = self.sender.frameToStringImage(self.noiseImage)

    def bind(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.TCP_IP, self.TCP_PORT))
            return True
        except:
            return False

    def run(self,channel):
        try:
            self.sock.send(str(channel))
            isChChanged = self.sock.recv(1)
            stringImage = self.sender.recvStringImage(self.sock,self.noiseImage)
        except Exception as e:
            self.sock.close()
            return (isChChanged,None)
        frame = self.sender.stringImageToFrame(stringImage)
        return (isChChanged,frame)


class SimCCTV():
    def __init__(self,ip,port,testvideos):
        self.TCP_IP = ip
        self.TCP_PORT = port

        self.sender = ImageTransmission()
        self.sock = socket.socket()
        self.sock = ssl.wrap_socket(self.sock,
                                   ca_certs="cipher/server.crt",
                                   cert_reqs=ssl.CERT_REQUIRED)
        self.sock.connect((self.TCP_IP, self.TCP_PORT))
        self.capture = cv2.VideoCapture(testvideos)


    def bind(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.TCP_IP, self.TCP_PORT))
            return True
        except:
            return False

    def run(self,channel):
        self.sock.send(str(channel))
        while True:
            try:
                self.sock.recv(1)
                ret, frame = self.capture.read()
                stringImage = self.sender.frameToStringImage(frame)
                self.sender.sendStringImage(self.sock, stringImage)
                if (cv2.waitKey(1) & 0xFF) == ord('q'):  # Hit `q` to exit
                    cv2.destroyAllWindows()
            except Exception as e:
                logging.ERROR(e)
                self.sock.close()


class SimBS():
    # loggingLevel = CRITICAL:4, ERROR:3, WARNING:2, INFO:1, DEBUG:0
    def __init__(self,tvPort,cctvPort,numOfCCTV):

        logging.basicConfig(level= logging.INFO)

        self.lock = threading.Lock()
        self.sender = ImageTransmission()

        self.cctvPort = cctvPort
        self.tvPort = tvPort
        self.numOfCCTV = numOfCCTV

        self.CCTVStringImage = []
        self.CCTVServer = None
        self.TVServer = None
        self.NoneImage = None

        default1 = cv2.imread("rsc/default.png")
        default1 = self.sender.frameToStringImage(default1)
        default2 = cv2.imread("rsc/default2.png")
        default2 = self.sender.frameToStringImage(default2)
        default3 = cv2.imread("rsc/default3.png")
        default3 = self.sender.frameToStringImage(default3)
        default4 = cv2.imread("rsc/default4.png")
        default4 = self.sender.frameToStringImage(default4)

        self.default = [default1,default2,default3,default4]

        try:
            self.initNoneImage()
            self.initCCTVStringImage()
            self.open()
        except:
            logging.ERROR("server start failed")
        logging.info("server start completed")

    def initNoneImage(self):
        self.NoneImage = cv2.imread("rsc/nosignal.png")
        self.NoneImage = self.sender.frameToStringImage(self.NoneImage)
        logging.info("initNoneImage() completed")

    def initCCTVStringImage(self):
        with self.lock:
            self.CCTVStringImage = [[False,self.NoneImage] for i in range(self.numOfCCTV)]
        print self.CCTVStringImage
        logging.info("initCCTVStringImage() completed")

    def setCCTVStringImage(self,channel,strimage):
        with self.lock:
            self.CCTVStringImage[int(channel)][1] = strimage

    def setTVCurrChannel(self,channel,onOff):
        with self.lock:
            self.CCTVStringImage[int(channel)][0] = onOff

    def setTVCurrChannelOff(self):
        with self.lock:
            for ch in range(len(self.CCTVStringImage)):
                self.CCTVStringImage[ch][0] = False

    def printTVCurrChannel(self):
        with self.lock:
            print self.CCTVStringImage[0][0] , self.CCTVStringImage[1][0] , self.CCTVStringImage[2][0]

    def getTVCurrChannel(self,channel):
        with self.lock:
            return self.CCTVStringImage[int(channel)][0]

    def getCCTVStringImage(self,channel):
        with self.lock:
            strimg = self.CCTVStringImage[channel][1]
        return strimg



    def open(self):
        try :
            bind_ip = '0.0.0.0'
            bind_port = self.cctvPort
            self.CCTVServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.CCTVServer.bind((bind_ip, bind_port))
            self.CCTVServer.listen(self.numOfCCTV)  # max backlog of connections

            bind_port = self.tvPort
            self.TVServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.TVServer.bind((bind_ip, bind_port))
            self.TVServer.listen(self.numOfCCTV)  # max backlog of connections
        except Exception as msg:
            logging.ERROR("self.open() 56 line : bind err" + msg)

        logging.info("open() completed")

    def handleCCTVConnection(self, client_sock,address):
        try:
            cctvChannel= client_sock.recv(1)
        except:
            client_sock.close()
            logging.info("Failed to receive channel information ")
            return 0
        logging.info(str(address)+ " ch : "+str(cctvChannel)+ " , Successful reception of channel information ")
        try:
            while True:
                while not self.getTVCurrChannel(cctvChannel):
                    time.sleep(2)
                else:
                    client_sock.send(cctvChannel)
                    stringImage = self.sender.recvStringImage(client_sock,self.NoneImage)
                    self.setCCTVStringImage(cctvChannel,stringImage)

        except Exception as e:
            logging.info("Failed to apply pictures received from CCTV to channel "+str(cctvChannel) + ", err msg:" +e)
        finally:
            self.setCCTVStringImage(cctvChannel,self.NoneImage)
            client_sock.close()
            logging.info("Apply that 'self.NoneImage' to Channel "+ str(cctvChannel))
            return 0

    def handleTVConnection(self, client_sock,address):
        i = 0
        temp = 0
        try:
            while True:
                i += 1
                currChannel = client_sock.recv(1)
                if currChannel != temp:
                    self.setTVCurrChannelOff()
                    temp = currChannel
                    client_sock.send('0')
                else:
                    client_sock.send('1')

                self.setTVCurrChannel(int(currChannel),True)
                stringImage = self.getCCTVStringImage(int(currChannel))
                if stringImage == self.NoneImage:
                    stringImage = self.default[i%4]
                self.sender.sendStringImage(client_sock,stringImage)
        except Exception as e:
            logging.info(str(address)+"channel information or picture transfer failed")
            client_sock.close()
            self.setTVCurrChannelOff()
            return


    def TVService(self):
        while True:
            client_sock, address = self.TVServer.accept()

            client_sock = ssl.wrap_socket(client_sock,
                                         server_side=True,
                                         certfile="cipher/server.crt",
                                         keyfile="cipher/server.key")
            logging.info(str(address)+ " TV connected to the server." )
            t = Thread(target=self.handleTVConnection, args=(client_sock, address))
            t.start()

    def CCTVService(self):
        while True:
            client_sock, address = self.CCTVServer.accept()
            client_sock = ssl.wrap_socket(client_sock,
                                         server_side=True,
                                         certfile="cipher/server.crt",
                                         keyfile="cipher/server.key")
            logging.info(str(address)+  " CCTV connected to the server." )
            t = Thread(target=self.handleCCTVConnection, args=(client_sock, address))
            t.start()

    def testprint(self):
        while True:
            self.printTVCurrChannel()
            time.sleep(0.5)
    def Service(self):
        TV = Thread(target=self.TVService, args=())
        CCTV = Thread(target=self.CCTVService, args=())
        thread.start_new_thread(self.testprint,())
        TV.start()
        CCTV.start()
        TV.join()
        CCTV.join()

import thread

if __name__=="__main__":
    sbs = SimBS(19200,19201,3)
    sbs.Service()