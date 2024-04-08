# -*- coding:utf-8 -*-
"""
@author zhangjian
"""
from collections import OrderedDict
from .base_render import BaseRender
from .date_render import DateRender
from .eng_render import EngRender
from .number_render import NumberRender
from .subaddr_render import SubAddrRender
from .task_render import TaskRender
from .sequence_render import SequenceRender


def getCorpusGenerate(logger, cfg):
    '''
    返回语料生成器
    '''

    cfg = cfg['TEXT']
    sample_size = cfg['SAMPLE']['SAMPLE_SIZE']

    # generators
    corpus = OrderedDict()
    corpus['corpus'] = BaseRender
    corpus['date'] = DateRender
    corpus['number'] = NumberRender
    corpus['sub_address'] = SubAddrRender
    corpus['eng_char'] = EngRender
    corpus['task'] = TaskRender
    corpus['sequence'] = SequenceRender

    generators = OrderedDict()
    for sample, amount in sample_size.items():
        assert sample in corpus

        if amount != 0:
            handler = corpus[sample](logger, cfg)
            generators[sample] = (handler, handler.generate(amount))

    return generators

