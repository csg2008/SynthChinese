# -*- coding:utf-8 -*-
"""
@author zhangjian
"""

import os
import random
from copy import deepcopy
from PIL import ImageFont
from typing import List, Set
from fontTools.ttLib import TTCollection, TTFont


class FontsFactory:
    def __init__(self, logger, font_dir, charset_check: bool = True, fonts_prob=None, whiteList: List[str] = None):
        self.logger = logger
        self.whiteList = whiteList
        self.charset_check = charset_check
        self.fonts_dict = self.get_all_fonts(font_dir)
        self._init_fonts_prob(fonts_prob)

    def _init_fonts_prob(self, fonts_prob):
        if fonts_prob:
            self.font_prob = fonts_prob
        else:
            # if fonts_prob not specified, use same prob for each font
            self.font_prob = {}
            for font in self.fonts_dict:
                self.font_prob[font] = 1

        # drop unsupported fonts
        stripKeys = set()
        for font in self.font_prob.keys():
            if font not in self.fonts_dict:
                stripKeys.add(font)
        if self.whiteList is not None:
            for font in self.font_prob.keys():
                if font not in self.whiteList:
                    stripKeys.add(font)
            for font in stripKeys:
                del self.font_prob[font]

    def get_all_fonts(self, resource_path):
        """
        traversal the resource dir, find all font files
        """

        font_dict = {}
        all_files = os.listdir(resource_path)
        # get file end with '.ttf'
        ttf_files = list(filter(lambda x: os.path.splitext(x)[1] in ['.ttf', '.otf', '.TTF', '.ttc'], all_files))
        for ttf in ttf_files:
            if self.whiteList and ttf not in self.whiteList:
                continue

            charset = self.get_font_charset(os.path.join(resource_path, ttf))
            font_dict[ttf] = (os.path.join(resource_path, ttf), charset)
        return font_dict

    def get_font(self, font_path: str, font_size: int) -> ImageFont.FreeTypeFont:
        """Get a FreeType font object"""

        font = ImageFont.truetype(font_path, font_size)
        return font

    def _load_font(self, font_path):
        """
        Read ttc, ttf, otf font file, return a TTFont object
        """

        # ttc is collection of ttf
        if font_path.endswith('ttc'):
            ttc = TTCollection(font_path)
            # assume all ttfs in ttc file have same supported chars
            return ttc.fonts[0]

        if font_path.endswith('ttf') or font_path.endswith('TTF') or font_path.endswith('otf'):
            ttf = TTFont(font_path, 0, allowVID=0,
                         ignoreDecompileErrors=True,
                         fontNumber=-1)

            return ttf

    def get_font_charset(self, font_path: str) -> Set[str]:
        try:
            ttf = self._load_font(font_path)
            chars_set = set()
            for table in ttf['cmap'].tables:
                for k, v in table.cmap.items():
                    char = chr(k)
                    chars_set.add(char)
        except Exception as e:
            chars_set = {}
            self.logger.exception(f'get_font_charset error: {e}, font path: {font_path}')

        return chars_set

    def get_supported_fonts(self, text: str, once: bool = False) -> dict:
        if self.charset_check:
            # drop unsupported charsets

            if once:
                fonts = list(self.font_prob.keys())

                random.shuffle(fonts)
                for font_name in fonts:
                    if font_name in self.fonts_dict:
                        num_hit = 0
                        for char in text:
                            if char in self.fonts_dict[font_name][1]:
                                num_hit += 1
                            else:
                                break

                        if num_hit == len(text):
                            return {font_name: self.font_prob[font_name]}
                    else:
                        self.logger.error(f'No such font in target dir: {font_name}')
            else:
                supported_fonts = deepcopy(self.font_prob)

                for char in text:
                    for font_name in list(supported_fonts.keys()):
                        if font_name in self.fonts_dict:
                            if char not in self.fonts_dict[font_name][1]:
                                supported_fonts.pop(font_name)
                        else:
                            self.logger.error(f'No such font in target dir: {font_name}')
        else:
            supported_fonts = self.font_prob

        return supported_fonts

    def generate_font(self, text):
        # get supported fonts
        supported_fonts = self.get_supported_fonts(text, True)

        # randomly choose one
        if supported_fonts:
            font_name = random.choices(list(supported_fonts.keys()), list(supported_fonts.values()), k=1)[0]
            font_file = self.fonts_dict[font_name][0]
        else:
            font_name = None
            font_file = None

        return font_name, font_file


if __name__ == '__main__':
    ff = FontsFactory('../../data/fonts')
    print(ff.generate_font('我们'))
