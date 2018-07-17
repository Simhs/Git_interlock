# 사용법

### 서버 ssh 접속시 종료후에도 계속 프로세스 실행 방법


```python
python tv.py <serv ip>
python cctv.py <serv ip> <channel 0~2 >
python server.py
```

```shell
sim@MacSoon:~$ ssh id@serverip
sim@11.111.111.111's password:
sim@ubuntu:~$ [프로그램 실행]
sim@ubuntu:~$ CTRL+Z
sim@ubuntu:~$ bg
sim@ubuntu:~$ disown
sim@ubuntu:~$ exit
```
