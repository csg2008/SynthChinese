# -*- coding:utf-8 -*-
"""
@author zhangjian
"""

import argparse
import datetime
from synth.corpus.base_corpus_factory import get_corpus
from synth.synth_pipeline import Pipeline


def parse_args():
    parser = argparse.ArgumentParser(description='Generate training data for OCR')
    parser.add_argument('--config_file', '-f', default='base.yaml', type=str,
                        help='config file name')
    parser.add_argument('--target_dir', '-t', default='samples',type=str,
                        help='The directory to store generated images')
    parser.add_argument('--category', '-c', default='train',  type=str,
                        help='The text file name used to store image file path and its labels')
    parser.add_argument('--label_sep', '-s', default='\t', type=str,
                        help='separator in label_file')
    arg_dict = parser.parse_args()

    return arg_dict


if __name__ == '__main__':
    import os
    import yaml
    arg_dict = parse_args()
    cfg = yaml.load(open('configs/' + arg_dict.config_file, encoding='utf-8'), Loader=yaml.FullLoader)
    # 获取语料
    corpus_generators = get_corpus(cfg)
    # 生成目录
    fname, _ = os.path.splitext(arg_dict.config_file)
    target_path = os.path.join(arg_dict.target_dir, fname + datetime.datetime.now().strftime('_%Y%m%d%H%M%S'))
    # 合成
    synthPipe = Pipeline(cfg, target_path, arg_dict.category, arg_dict.label_sep, display_interval=2000)
    for corp in corpus_generators:
        print(f'Start with {corp}')
        synthPipe(corpus_generators[corp], corp[0].upper())

