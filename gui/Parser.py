class Parser:
    def __init__(self, data, new_div=','):
        self.buf = data
        self.div = new_div
        self.str = None

    def set_div(self, new_div):
        self.div = new_div

    def clear(self):
        if self.str:
            del self.str
        self.str = None

    def amount(self):
        if not self.buf:
            return 0
        count = 1
        p = self.buf
        while p:
            if p == self.div:
                count += 1
            p += 1
        return count

    def split(self):
        self.len = self.amount()
        self.clear()
        self.str = [None] * self.len
        if not self.str:
            return 0
        self.str[0] = self.buf
        i = 0
        j = 0
        while self.buf[i]:
            if self.buf[i] == self.div:
                self.buf[i] = '\0'
                self.str[j + 1] = self.buf[i + 1]
            i += 1
        return self.len

    def restore(self):
        for i in range(self.len - 1):
            self.str[i] += self.div

    def get_int(self, num):
        return int(self.str[num])

    def get_float(self, num):
        return float(self.str[num])

    def equals(self, num, comp):
        return self.str[num] == comp

    def parse_longs(self, data):
        if not self.buf:
            return 0
        count = 0
        offset = self.buf
        while True:
            data[count] = int(offset)
            count += 1
            offset = offset.find(self.div)
            if offset:
                offset += 1
            else:
                break
        return count

    def parse_ints(self, data):
        if not self.buf:
            return 0
        count = 0
        offset = self.buf
        while True:
            data[count] = int(offset)
            count += 1
            offset = offset.find(self.div)
            if offset:
                offset += 1
            else:
                break
        return count

    def parse_bytes(self, data):
        if not self.buf:
            return 0
        count = 0
        offset = self.buf
        while True:
            data[count] = int(offset)
            count += 1
            offset = offset.find(self.div)
            if offset:
                offset += 1
            else:
                break
        return count

    def __getitem__(self, idx):
        return self.str[idx]



