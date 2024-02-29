# -*- coding:utf-8 -*-
"""
@author zhangjian
"""
from collections import OrderedDict
from synth.corpus.corpus_factory.base_render import BaseRender
from synth.corpus.corpus_factory.date_render import DateRender
from synth.corpus.corpus_factory.eng_render import EngRender
from synth.corpus.corpus_factory.id_render import IDRender
from synth.corpus.corpus_factory.number_render import NumberRender
from synth.corpus.corpus_factory.subaddr_render import SubAddrRender
from synth.corpus.corpus_factory.task_render import TaskRender
from synth.corpus.corpus_factory.sequence_render import SequenceRender


def get_corpus(cfg):
    cfg = cfg['TEXT']
    sample_size = cfg['SAMPLE']['SAMPLE_SIZE']
    # corpus
    task_render = TaskRender()
    corpus_render = BaseRender(cfg['SAMPLE']['CHAR_SET'], cfg)
    date_render = DateRender(cfg['SAMPLE']['CHAR_SET'])
    number_render = NumberRender(cfg['SAMPLE']['CHAR_SET'])
    eng_render = EngRender(cfg['SAMPLE']['CHAR_SET'])
    id_render = IDRender(cfg['SAMPLE']['CHAR_SET'])
    sub_addr_render = SubAddrRender(cfg['SAMPLE']['CHAR_SET'])
    sequence_render = SequenceRender(cfg['SAMPLE']['CHAR_SET'], cfg)

    all_renders = OrderedDict()
    all_renders['corpus'] = corpus_render
    all_renders['date'] = date_render
    all_renders['number'] = number_render
    all_renders['sub_address'] = sub_addr_render
    all_renders['id'] = id_render
    all_renders['eng_char'] = eng_render
    all_renders['task'] = task_render
    all_renders['sequence'] = sequence_render

    all_generators = OrderedDict()
    for render_name in all_renders:
        amount = sample_size[render_name]

        if amount != 0:
            all_generators[render_name] = all_renders[render_name].generate(amount)

    return all_generators

