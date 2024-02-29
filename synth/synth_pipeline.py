# -*- coding:utf-8 -*-
"""
@author zhangjian
"""
import os
import re
import cv2
import datetime
from synth.utils.font_util import FontUtil
from synth.utils.cv_util import cvUtil
from synth.utils.merge_util import MergeUtil
from synth.logger.synth_logger import logger


class Pipeline:
    blank_compress_pattern = re.compile(' +')

    def __init__(self, cfg, target_dir, label_file, label_sep='\t', compress_blank=True, display_interval=2000):
        self.font_util = FontUtil(cfg)
        self.cv_util = cvUtil(cfg)
        self.merge_util = MergeUtil(cfg)

        self.target_dir = target_dir
        self.img_dir = self._init_img_dir()
        self.label_file = open(self.check_filename(os.path.join(target_dir, label_file)), 'w')
        self.label_sep = label_sep
        self.comp_blank = compress_blank

        self.display_interval = display_interval

    def __del__(self):
        # save label
        self.label_file.close()

    def _init_img_dir(self):
        times = 1
        datestr = datetime.datetime.now().strftime('%Y_%m_%d')
        while True:
            test_num_str = '{:0>3}'.format(times)
            tmp_dirname = datestr + '_' + test_num_str
            if os.path.exists(os.path.join(self.target_dir, tmp_dirname)):
                times += 1
            else:
                img_dir = os.path.join(self.target_dir, tmp_dirname)
                os.makedirs(img_dir)
                logger.info('A new train images directory has been generated: {}'.format(self.target_dir + '/' + tmp_dirname))
                self.img_dir_short = tmp_dirname
                return img_dir

    def check_filename(self, file_name):
        if os.path.exists(file_name):
            (shotname, extension) = os.path.splitext(file_name)
            times = 2
            while True:
                tmp_path = shotname + '_' + str(times) + extension
                if os.path.exists(tmp_path):
                    times += 1
                else:
                    logger.info(f'{file_name} has existed, a new log file {tmp_path} has been created.')
                    return tmp_path
        else:
            return file_name

    def compress_blank(self, text):
        compressed_text = self.blank_compress_pattern.sub('', text)
        return compressed_text

    def img_save(self, text, f_meta, f_name, img):
        # save img
        cv2.imwrite(os.path.join(self.img_dir, f_name), img)
        # compress blanks in label
        if self.comp_blank:
            text = self.compress_blank(text)
        # strip
        text = text.strip()
        # save label
        label_str = f'{self.img_dir_short}/{f_name}{self.label_sep}{text}{self.label_sep}{f_meta}\n'
        self.label_file.write(label_str)

    def __call__(self, corpus_generator, corpus_type='C'):
        count = 0
        for text in corpus_generator:

            try:
                font_str, font_img = self.font_util(text)
                cv_str, cv_img = self.cv_util(font_img)
                mg_str, mg_img = self.merge_util(cv_img)

                f_name = f'{corpus_type}{count:0>8}.jpg'
                f_meta = f'{font_str}_{cv_str}_{mg_str}'
                self.img_save(text, f_meta, f_name, mg_img)

                count += 1

                if count % self.display_interval == 0:
                    logger.info(f'Num: {count:0>8} image has been generated.')
            except:
                logger.exception('')
