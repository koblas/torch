from torch.redis import Client
from tornado import ioloop

client = Client()
loop = ioloop.IOLoop.instance()

TEST = [
    ['flushall', lambda c, cb: c.flushall(callback=cb), True],
    ['publish', lambda c, cb: c.publish('test', 'foo', callback=cb), 1],
    ['publish', lambda c, cb: c.publish('test', 'foo2', callback=cb), 1],
    ['publish', lambda c, cb: c.publish('test', 'foo4', callback=cb), 1],
]

def connected(c):
    print "HERE", c

    def run_next(c, args):
        t = TEST.pop(0)
        if t[2] == args:
            print "OK ", t[0], args
        else:
            print "** ", t[0], args

        if TEST:
            TEST[0][1](c, run_next)
        else:
            loop.stop()

    TEST[0][1](c, run_next)

client.connect(connected)

loop.start()
