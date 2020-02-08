from ..httpsocket import HttpHeader, HttpSocket

header = HttpHeader()
print(header._header)
print('Connection' in header)

header.add('Connection', 'keep-alive')
print('Connection' in header)

header.add('X-Requested-With', 'XMLHttpRequest')

for k, v in header.items():
    print(f"{k}: {v}")

with HttpSocket("124.228.42.248", 80) as socket:
    print(socket.get_http('/'))