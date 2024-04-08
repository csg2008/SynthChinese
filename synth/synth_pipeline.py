# -*- coding:utf-8 -*-
"""
@author zhangjian
"""
import os
import re
import cv2
import html
from .corpus import getCorpusGenerate
from .libs.misc import generateImagePreviews
from .libs.bg_factory import bgFactory
from .utils.font_util import FontUtil
from .utils.cv_util import cvUtil
from .utils.merge_util import MergeUtil


class Pipeline:
    blank_compress_pattern = re.compile(' +')

    def __init__(self, cfg, logger, target_dir: str, category: str, label_index: bool = False, seq: int = 1, display_interval: int = 2000):
        os.makedirs(target_dir, exist_ok=True)

        self.cv_util = cvUtil(cfg)
        self.font_util = FontUtil(cfg, logger)
        self.merge_util = MergeUtil(cfg, logger)
        self.bg_factory = bgFactory(cfg['BACKGROUND'])

        self.cfg = cfg
        self.seq = seq
        self.logger = logger
        self.label_index = label_index
        self.category = category
        self.target_dir = target_dir
        self.img_dir_short = 'img'
        self.img_dir = os.path.join(target_dir, self.img_dir_short)
        self.label_file = open(self.check_filename(os.path.join(target_dir, category + '.txt')), 'w', encoding='utf-8')
        self.label_sep = cfg['TEXT']['SAMPLE']['SEPARATOR']
        self.compress_blank = cfg['TEXT']['SAMPLE']['COMPRESS_BLANK']

        self.display_interval = display_interval

        os.makedirs(self.img_dir, exist_ok=True)

    def __del__(self):
        # save label
        self.label_file.close()

    def check_filename(self, file_name: str) -> str:
        if os.path.exists(file_name):
            (basename, extension) = os.path.splitext(file_name)
            times = 2
            while True:
                tmp_path = basename + '_' + str(times) + extension
                if os.path.exists(tmp_path):
                    times += 1
                else:
                    self.logger.info(f'{file_name} has existed, a new log file {tmp_path} has been created.')
                    return tmp_path
        else:
            return file_name

    def compress_blank_char(self, text: str) -> str:
        return self.blank_compress_pattern.sub('', text)

    def img_save(self, text, f_meta, f_name, img, label_idx = False):
        # save img
        cv2.imwrite(os.path.join(self.img_dir, f_name), img)
        # compress blanks in label
        if self.compress_blank and not label_idx:
            text = self.compress_blank_char(text)
        # strip
        text = text.strip()
        # save label
        label_str = f'{self.img_dir_short}/{f_name}{self.label_sep}{text}{self.label_sep}{f_meta}\n'
        self.label_file.write(label_str)

    def generator(self, corpus_generator, corpus_type='C', imgs = []):
        for text in corpus_generator[1]:

            try:
                bg_name, bg_img =self.bg_factory.generate_bg()
                font_str, font_img = self.font_util(text, bg_img)
                cv_str, cv_img = self.cv_util(font_img)
                mg_str, mg_img = self.merge_util(bg_name, bg_img, cv_img)
                # cv_str = 'cv'
                # mg_str = 'mg'
                # mg_img = font_img

                f_name = f'{self.category}-{corpus_type}{self.seq:0>8}.jpg'
                f_meta = f'{font_str}_{cv_str}_{mg_str}'

                if self.label_index:
                    self.img_save(corpus_generator[0].transfer_label_to_index(text), f_meta, f_name, mg_img, self.label_index)
                else:
                    self.img_save(text, f_meta, f_name, mg_img)

                self.seq += 1
                imgs.append(f'<img src="{self.img_dir_short}/{f_name}" alt="{html.escape(text)}" title="{html.escape(text)}" />')

                if self.seq % self.display_interval == 0:
                    self.logger.info(f'Num: {self.seq:0>8} image has been generated.')
            except:
                self.logger.exception('')

    def run(self):
        imgs = []

        # 获取语料生成器
        generators = getCorpusGenerate(self.logger, self.cfg)

        # 开始生成数据
        for generator in generators:
            self.logger.info(f'Start generator with {generator}')
            self.generator(generators[generator], generator[0].upper(), imgs = imgs)

        generateImagePreviews(os.path.join(self.target_dir, f'preview-{self.category}.html'), imgs)
        self.logger.info('ocr train data generate finish!')
