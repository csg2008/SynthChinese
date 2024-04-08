import random
from .base_render import BaseRender


class SequenceRender(BaseRender):
    """
    基于字符列表的排列组合生成器
    """
    def __init__(self, logger, cfg=None):
        super(SequenceRender, self).__init__(logger, cfg)

        self.last = 0
        self.charsList = list(self.chars)

    def get_sample(self):
        while True:
            num = random.randint(self.length[0], self.length[1])
            if self.last + num >= len(self.charsList):
                self.last = 0
            if self.last + num >= len(self.charsList) or self.last == 0:
                random.shuffle(self.charsList)

            if num == 0:
                num = 1

            part = ''.join(self.charsList[self.last : self.last + num])

            self.last = self.last + num

            if part.startswith(' ') or part.endswith(' '):
                continue

            return part

    def generate(self, size):
        num = 0
        while True:
            yield self.get_sample()
            num += 1
            if num >= size:
                return


if __name__ == '__main__':
    r = SequenceRender('../data/chars/eng.txt')
    words = r.generate(10)
    print(words)