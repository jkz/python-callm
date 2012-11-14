class Response(object):
    status = 200
    index = 0

    def __init__(self, response, headers={}):
        self.response = response
        self.closed = False
        self.headers = headers

    def __len__(self):
        return len(self.data)

    def getheaders(self):
        return self.headers

    @property
    def raw(self):
        return self.data

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = str(self.response)
        return self._data

    def isclosed(self):
        return self.closed

    def read(self, amount=0):
        if not amount:
            return self.read(len(self))
        if self.index + amount > len(self):
            raise Exception('Too much data requested')
        if self.index + amount < len(self):
            data = self.data[self.index:self.index+amount]
            self.index += amount
            return data
        self.closed = True
        return self.data[self.index:]

class StreamResponse(Response):
    max_reads = 5
    reads = 0

    def isclosed(self):
        return self.closed

    def get_byte(self):
        c = self.data[self.index]
        self.index += 1
        if self.index == len(self):
            self.reads += 1
            self.index = 0
        if self.reads == self.max_reads:
            self.closed = True
            #raise CreekError('Stream closed')
        return c

    def read(self, amount=10):
        if not amount:
            amount = len(self)
        data = ''
        for x in range(amount):
            data += self.get_byte()
        return data


class Connection(object):
    def __init__(self, host):
      self.host = host

    def request(self, method, url, body="", headers={}):
        self.response = {
              'method': method,
              'url': url,
              'body': body,
              'headers': headers}

    def getresponse(self):
        return Response(self.response)

class StreamConnection(Connection):
    pass
