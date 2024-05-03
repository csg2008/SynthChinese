"""
@author zhangjian
some functions refers to: https://github.com/Sanster/text_renderer
"""

import cv2
import random
import numpy as np
from typing import Tuple, Union
from PIL import ImageDraw, Image

from ..libs.font_text import FontText, FontColor
from ..libs.math_util import get_random_value
from ..libs.fonts_factory import FontsFactory

def transparent_img(size: Tuple[int, int]) -> Image.Image:
    """

    Args:
        size: (width, height)
    Returns:

    """
    return Image.new("RGB", (size[0], size[1]), (0, 0, 0))


def draw_text_on_bg(
    font_text: FontText,
    text_color: FontColor,
    char_spacing: Union[float, Tuple[float, float]] = -1,
) -> Image.Image:
    """

    Parameters
    ----------
    font_text : FontText
    text_color : RGBA
        Default is black
    char_spacing : Union[float, Tuple[float, float]]
        Draw character with spacing. If tuple, random choice between [min, max)
        Set -1 to disable

    Returns
    -------
        Image.Image:
            RGBA Pillow image with text on a transparent image
    -------

    """
    if char_spacing == -1:
        if font_text.horizontal:
            return _draw_text_on_bg(font_text, text_color)
        else:
            char_spacing = 0

    chars_size = []
    widths = []
    heights = []

    for c in font_text.text:
        size = font_text.font.getbbox(c)[2:]
        chars_size.append(size)
        widths.append(size[0])
        heights.append(size[1])

    if font_text.horizontal:
        width = sum(widths)
        height = max(heights)
    else:
        width = max(widths)
        height = sum(heights)

    char_spacings = []

    cs_height = font_text.size[1]
    for i in range(len(font_text.text)):
        if isinstance(char_spacing, list) or isinstance(char_spacing, tuple):
            s = np.random.uniform(*char_spacing)
            char_spacings.append(int(s * cs_height))
        else:
            # char_spacings.append(int(char_spacing * cs_height))
            char_spacings.append(int(char_spacing))

    if font_text.horizontal:
        width += sum(char_spacings[:-1])
    else:
        height += sum(char_spacings[:-1])

    text_mask = transparent_img((width, height))
    draw = ImageDraw.Draw(text_mask)

    c_x = 0
    c_y = 0

    if font_text.horizontal:
        y_offset = font_text.offset[1]
        for i, c in enumerate(font_text.text):
            draw.text((c_x, c_y - y_offset), c, fill=text_color, font=font_text.font)
            c_x += chars_size[i][0] + char_spacings[i]
    else:
        x_offset = font_text.offset[0]
        for i, c in enumerate(font_text.text):
            draw.text((c_x - x_offset, c_y), c, fill=text_color, font=font_text.font)
            c_y += chars_size[i][1] + char_spacings[i]
        text_mask = text_mask.rotate(90, expand=True)

    return text_mask

def _draw_text_on_bg(
    font_text: FontText,
    text_color: FontColor,
) -> Image.Image:
    """
    Draw text

    Parameters
    ----------
    font_text : FontText
    text_color : RGBA
        Default is black

    Returns
    -------
        Image.Image:
            RGBA Pillow image with text on a transparent image
    """
    text_width, text_height = font_text.size
    text_mask = transparent_img((text_width, text_height))
    draw = ImageDraw.Draw(text_mask)

    xy = font_text.xy

    # TODO: figure out anchor
    draw.text(
        xy,
        font_text.text,
        font=font_text.font,
        fill=text_color,
        anchor=None,
    )

    return text_mask

class FontUtil(object):
    def __init__(self, cfg, logger):
        """
        :param cfg:

        # cfg of font
        fonts_dir: dir of font files
        fonts: {font_short_name: font_prob,...} like {'courbd1.7': 0.5, 'courbd1.7': 0.2}

        # cfg of surface
        size: [H, W]

        # cfg of font style
        'size': size of font : [min, max, type(uniform,gaussian)]
        'oblique': prob of oblique : [prob]
        'rotation': prob of rotation and degrees range: [prob, [-360, 360,type(uniform,gaussian)]]
        'strong': : prob of strong style: [prob]
        'wide': prob of wide style: [prob]
        'strength': strength of wide and strong style: [0, 1, type(uniform,gaussian)]
        'underline': [and 'underline_adjustment']: prob of underline style and underline adjustment factor: [prob, [0, 2], type(uniform,gaussian)]
        """

        self.logger = logger
        self.char_space = float(cfg['EFFECT']['FONTS']['char_space'])
        self.font_cfg = cfg['EFFECT']['FONTS']
        self.font_style_cfg = self.font_cfg['STYLE']

        # init font factory
        fontCache = self.font_cfg['cache'] if 'cache' in self.font_cfg else False
        fontsProb = self.font_cfg['fonts_prob'] if 'fonts_prob' in self.font_cfg else None
        fontWhiteList = self.font_cfg['white_list'] if 'white_list' in self.font_cfg else None
        charsetCheck = self.font_cfg['charset_check'] if 'charset_check' in self.font_cfg else True
        self.fontFac = FontsFactory(logger, self.font_cfg['fonts_dir'], fontCache, charsetCheck, fontsProb, fontWhiteList)

    def __call__(self, text, bg_img):
        font_name, font_file = self.fontFac.generate_font(text)

        # size
        size = int(get_random_value(*self.font_style_cfg['size']))

        # 文字颜色（融合失败，暂时用默认颜色）
        # textColor = self.get_text_color(bg_img)
        textColor = (255, 255, 255)

        # text direction
        vertical = len(text) <= self.font_style_cfg['vertical'][1] and random.random() < self.font_style_cfg['vertical'][0]

        return self.renderText(text, font_name, font_file, size, not vertical, textColor)


    def renderText(self, text: str, font_name:str, font_file: str, size: int, horizontal: bool, text_color: FontColor = (255, 255, 255)) -> Tuple[str, np.ndarray]:
        font = self.fontFac.get_font(font_file, size)
        font_text = FontText(font, text, font_name, horizontal)

        text_mask = draw_text_on_bg(font_text, text_color, self.char_space)

        np_img = cv2.cvtColor(np.array(text_mask), cv2.COLOR_RGB2BGR)
        font_string = f'font{size}{font_name}_horizontal{int(horizontal)}'

        return font_string, np_img

    def get_text_color(self, bg: Image.Image) -> FontColor:
        # TODO: better get text color
        # text_mask = self.draw_text_on_transparent_bg(text, font)
        np_img = np.array(bg)
        # mean = np.mean(np_img, axis=2)
        mean = np.mean(np_img)

        r = np.random.randint(0, int(mean * 0.7))
        g = np.random.randint(0, int(mean * 0.7))
        b = np.random.randint(0, int(mean * 0.7))
        fg_text_color = (r, g, b)

        return fg_text_color

    # def __call1__(self, text):
    #     font_name, font_file = self.fontFac.generate_font(text)
    #     # size
    #     size = int(get_random_value(*self.font_style_cfg['size']))
    #     font = freetype.Font(font_file, size=int(size))
    #     # oblique
    #     if random.random() < self.font_style_cfg['oblique']:
    #         font.oblique = True
    #     # rotation
    #     if random.random() < self.font_style_cfg['rotation'][0]:
    #         degree = get_random_value(*self.font_style_cfg['rotation'][1])
    #         degree = int(degree)
    #         font.rotation = degree
    #     if font_name not in self.font_cfg['fonts_strong_false']:
    #         """
    #         some fonts not suitable for strong effect
    #         """
    #         # strong
    #         if random.random() < self.font_style_cfg['strong']:
    #             font.strong = True
    #         # wide (not support rotated)
    #         if font.rotation == 0 and font.strong == False:
    #             if random.random() < self.font_style_cfg['wide']:
    #                 font.wide = True
    #         # strength
    #         if font.strong or font.wide:
    #             strength = get_random_value(*self.font_style_cfg['strength'])
    #             strength = round(strength, 2)
    #             font.strength = strength

    #     # underline (not support rotated)
    #     if font.rotation == 0:
    #         if random.random() < self.font_style_cfg['underline'][0]:
    #             font.underline = True
    #             adj_factor = get_random_value(*self.font_style_cfg['underline'][1])
    #             adj_factor = round(adj_factor, 2)
    #             font.underline_adjustment = adj_factor

    #     # render to surface
    #     surf, rect = font.render(text)
    #     if rect.height <= (size * 0.6):
    #         # height too small like '-', use size as height
    #         surf = pygame.Surface((rect.width, size), pygame.locals.SRCALPHA, 32)
    #         font.render_to(surf, (0, int((size-rect.height)/2)), text)

    #     arr = pygame.surfarray.pixels_alpha(surf).swapaxes(0, 1)  # 获取图像的透明度（当render_to只传fgcolor背景就是透明的，值为0）

    #     # str
    #     font_name_str = os.path.splitext(font_name)[0]
    #     font_string = f'font{size}{font_name_str}_oblique{int(font.oblique)}_rotation{font.rotation}_strong{int(font.strong)}_wide{int(font.wide)}_strength{round(font.strength,2)}_underline{int(font.underline)}{font.underline_adjustment}'

    #     return font_string, arr

    def __str__(self):
        pass

    def play(self, FPS=5):
        import cv2
        text = '安立路319号abcDEF'

        while True:
            font_str, font_img = self.__call__(text)
            cv2.namedWindow('Play', 0)
            cv2.resizeWindow('Play', 400, 100)
            cv2.imshow('Play', 255-font_img)
            key = cv2.waitKey(int(1000/FPS))
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite('./demo_img/'+font_str+'.jpg', 255-font_img)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    import yaml

    cfg = yaml.load(open('../../configs/base.yaml', encoding='utf-8'), Loader=yaml.FullLoader)
    cfg['EFFECT']['FONTS']['fonts_dir'] = '../../data/fonts'
    FU = FontUtil(cfg)
    FU.play(3)
