import HomeTV
import sys

if len(sys.argv) >= 3:
    server_ip = sys.argv[1]
    channel = int(sys.argv[2])
elif len(sys.argv) >= 2:
    server_ip = sys.argv[1]
    channel = 0

    print "sys.argv[2] has no data"
    print "you have to put channel after file"
    print "lkie : python cctv.py <serv ip> <channel> "
    print "Now excute : python tv.py "+ sys.argv[1]+" 0"
elif len(sys.argv) >= 1:
    server_ip = 'localhost'
    channel = 0
    print "sys.argv[1] has no data"
    print "sys.argv[2] has no data"
    print "you have to put ip and channel after file"
    print "lkie : python cctv.py <serv ip> <channel> "
    print "Now excute : python tv.py localhost 0"


stv = HomeTV.SimCCTV(server_ip,19201,0)
stv.run(0)