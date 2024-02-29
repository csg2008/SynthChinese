import copy
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
        okLines = []
        curLines = []
        preLines = copy.deepcopy(self.chars)

        for _ in range(self.length[1]):
            for pre in preLines:
                for cur in self.chars:
                    word = pre + cur
                    curLines.append(word)

                    if len(word) >= self.length[0] and not word.startswith(' ') and not word.endswith(' '):
                        num += 1
                        okLines.append(word)

                    if size > 0 and num >= size:
                        return okLines

            preLines = copy.deepcopy(curLines)
            curLines = []

        return okLines


if __name__ == '__main__':
    r = SequenceRender('../data/chars/eng.txt')
    words = r.generate(10)
    print(words)