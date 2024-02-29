import copy
import random
from synth.corpus.corpus_factory.base_render import BaseRender


class SequenceRender(BaseRender):
    """
    基于字符列表的排列组合生成器
    """
    def __init__(self, chars_file, cfg=None):
        super(SequenceRender, self).__init__(chars_file, cfg)

    def get_sample(self):
        pass

    def generate(self, size):
        num = 0
        charCnt = {}
        okLines = []
        curLines = []
        chars = list(self.chars)
        charsLen = len(self.chars)
        reGenLen = charsLen * 3
        preLines = copy.deepcopy(chars)
        preLineMax = max(int(len(chars) * 1.8), 10000)

        for _ in range(self.length[1]):
            for pre in preLines:
                for cur in chars:
                    if self.char_max_amount > 0:
                        if cur not in charCnt:
                            charCnt[cur] = 0
                        charCnt[cur] += 1

                        if charCnt[cur] > self.char_max_amount:
                            continue

                    word = pre + cur
                    curLines.append(word)

                    if not word.startswith(' ') and not word.endswith(' '):
                        num += 1
                        okLines.append(word)

                    if size > 0 and num >= size:
                        return okLines

            curLineLen = len(curLines)
            if charsLen >= 16 and curLineLen > preLineMax:
                random.shuffle(curLines)
                preLines = copy.deepcopy(curLines[:preLineMax])
            elif charsLen >= 16 and curLineLen > reGenLen:
                random.shuffle(curLines)
                preLineIdx = int(curLineLen * 0.25)
                preLines = copy.deepcopy(curLines[preLineIdx:])
            else:
                preLines = copy.deepcopy(curLines)

            curLines = []

        return okLines


if __name__ == '__main__':
    r = SequenceRender('../data/chars/eng.txt')
    words = r.generate(10)
    print(words)