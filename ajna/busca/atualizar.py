import http.client
import time


conn = http.client.HTTPConnection('localhost:8000')
conn.request('GET', '/busca/trataagendamentos/')
print(conn.getresponse().read())
time.sleep(10)
conn = http.client.HTTPConnection('localhost:8000')
conn.request('GET', '/busca/exportabson/')
print(conn.getresponse().read())
