# -*- coding:utf-8 -*-
"""
some functions refers to: https://github.com/Sanster/text_renderer
"""

from typing import Tuple

from PIL.ImageFont import FreeTypeFont

FontColor = Tuple[int, int, int]

class FontText:
    def __init__(self, font: FreeTypeFont, text: str, font_path: str, horizontal: bool = True):
        self.font = font
        self.text = text
        self.font_path = font_path
        self.horizontal = horizontal
        self.text_box = self.font.getbbox(self.text)
        self.text_mask_box = self.font.getmask(self.text).getbbox()

    @property
    def xy(self):
        """返回文字左上角坐标"""

        return 0 - self.text_box[0] - self.text_mask_box[0], 0 - self.text_box[1]

    @property
    def offset(self):
        """返回文字右下角坐标"""

        return self.text_box[:2]

    @property
    def size(self) -> Tuple[int, int]:
        """
        返回文字实际宽度和高度
        Returns:
            width, height
        """
        if self.horizontal:
            height = self.text_box[3] - self.text_box[1]
            return self.text_mask_box[2] - self.text_mask_box[0], height
        else:
            widths = [self.font.getbbox(c)[2] - self.font.getbbox(c)[0] for c in self.text]
            width = max(widths)
            height = sum([self.font.getbbox(c)[3] for c in self.text]) - self.font.getbbox(self.text[0])[1]
            return height, width
