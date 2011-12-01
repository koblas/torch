from tornado.testing import AsyncTestCase
from functools import partial
from torch.redis import Client
from tornado import ioloop
from tornado import gen

#  RUN WITH
#
#  python -m tornado.testing test.unit2
#
class RedisTestCase(AsyncTestCase):
    longMessage = True

    def test_hgetall(self):
        client = Client(io_loop=self.io_loop)
        client.connect(callback=self.stop)
        self.wait()

        TEST2 = [
            ['flushall', (client.flushall,), True],
            ['hset',     (client.hset, 'foohsh', 'foo', 'bar'), 1],
            ['hset',     (client.hset, 'foohsh', 'foo', 'bar'), 0],
            ['hset',     (client.hset, 'foohsh', 'gig', 'gog'), 1],
            ['hgetall',  (client.hgetall, 'foohsh'), {'foo':'bar','gig':'gog'}],
        ]

        for name, args, expect in TEST2:
            args[0](*args[1:], callback=lambda c, r: self.stop(r))
            response = self.wait()
            self.assertEqual(expect, response, name)
