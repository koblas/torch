from torch.redis import Client
from tornado import ioloop

client = Client()
loop = ioloop.IOLoop.instance()

def set_msg(c, msg):
    print "SET", msg

def got_msg(c, msg):
    print "GOT MSG", msg
    c.set('test', 'cat', callback=set_msg)
    c.subscribe('testX', got_msg)

def connected(c):
    c.subscribe('test', got_msg)

client.connect(connected)

loop.start()
