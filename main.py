# -*- coding:utf-8 -*-
"""
@author zhangjian
"""

import argparse
import os
import html
import datetime
import traceback
import yaml
import cv2

from synth.utils.logger import Logger
from synth.utils.font_util import FontUtil
from synth.libs.fonts_factory import FontsFactory
from synth.libs.misc import read_charset, generateImagePreviews
from synth.synth_pipeline import Pipeline

APP_PATH = os.path.dirname(os.path.abspath(__file__))

def parse_args():
    """解析命令行参数选项"""

    parser = argparse.ArgumentParser(description='OCR 训练数据生成器')
    parser.add_argument('--entry', '-e', type=str, required=True,
                        help="""命令入口, 如:
                        rec 生成文本识别数据集
                        preview 生成字体预览图
                        stat 统计 vocab 字库中的字符在字体文件中的次数
                        check 检查字体是否包含 vocab 文件中的字符""")
    parser.add_argument('--config_file', '-c', type=str,
                        help='配置文件路径')
    parser.add_argument('--output', '-o',type=str,
                        help='数据输出文件夹')
    parser.add_argument('--font_dir', '-f', type=str,
                        help='字体文件夹路径')
    parser.add_argument('--font_size', default=38, type=int,
                        help='预览字体大小')
    parser.add_argument('--category', default='train',  type=str,
                        help='生成的训练数据类别')
    parser.add_argument('--label_sep', default='\t', type=str,
                        help='数据标签分隔符')
    parser.add_argument('--index_start', default=1, type=int,
                        help='图片文件名序号起始值')
    parser.add_argument('--show_support', default=False, type=bool,
                        help='显示支持的字体列表，默认显示不支持的列表')
    parser.add_argument('--clean', default=False, type=bool,
                        help='是否清理不支持的字体文件')
    return parser.parse_args()

def stat_vocab(logger: Logger, config: str, font_dir: str):
    """
    统计 vocab 字库中的字符在字体中出现的次数

    args:
        logger: 日志
        config: 生成配置文件名
        font_dir: 字体文件夹路径
    """

    stat = {}
    cfg = yaml.load(open(config, 'r', encoding='utf-8'), Loader=yaml.FullLoader)
    chars = read_charset(cfg['TEXT']['SAMPLE']['CHAR_SET'])[0]
    whiteList = cfg['EFFECT']['FONTS']['white_list'] if 'white_list' in cfg['EFFECT']['FONTS'] else None
    ff = FontsFactory(logger, font_dir, charset_check = True, whiteList = whiteList)
    allFonts = ff.get_load_fonts()

    for char in chars:
        for font in allFonts.items():
            if char in font[1][1]:
                if char in stat:
                    stat[char] += 1
                else:
                    stat[char] = 1
            else:
                if char not in stat:
                    stat[char] = 0

    msg = []
    stat_list = []
    for k, v in stat.items():
        stat_list.append((k, v))
    stat_list.sort(key=lambda x: x[1])

    msg.append(f'vocab 字库中的字符在字体中出现的次数, 按出现次数排序(共 {len(allFonts)} 个字体):')
    for char, count in stat_list:
        msg.append(f'{char}: {count}')

    open('stat.txt', 'w+', encoding='utf-8').write('\n'.join(msg))

def check(logger: Logger, config: str, font_dir: str, show_support: bool, clean: str):
    """
    检查字体是否包含 vocab 文件中的字符

    args:
        logger: 日志
        config: 生成配置文件名
        font_dir: 字体文件夹路径
        show_support: 显示支持的字体列表，默认显示不支持的列表
        clean: 是否清理不支持的字体文件
    """

    cfg = yaml.load(open(config, 'r', encoding='utf-8'), Loader=yaml.FullLoader)
    chars = read_charset(cfg['TEXT']['SAMPLE']['CHAR_SET'])[0]
    whiteList = [os.path.basename(font_dir)] if os.path.isfile(font_dir) else None

    if whiteList is None:
        ff = FontsFactory(logger, font_dir, charset_check = True, whiteList = whiteList)
        allFonts = ff.get_all_fonts(font_dir)
        supportFonts = ff.get_supported_fonts(chars)
        numSupport, numAll = len(supportFonts), len(allFonts)
        if numSupport == numAll:
            logger.info('all fonts check done, pass!')
        else:
            support = []
            notSupport = []
            for fn in allFonts:
                if fn in supportFonts:
                    support.append(fn)
                else:
                    notSupport.append(fn)
                    if clean:
                        os.remove(os.path.join(font_dir, fn))

        if show_support:
            logger.info(f'all support fonts: {support}')
        else:
            logger.info(f'check done {numSupport}/{numAll}, not support fonts: {notSupport}')
    else:
        support = []
        notSupport = []
        ff = FontsFactory(logger, os.path.dirname(font_dir), charset_check = True, whiteList = whiteList)
        font_charsets = ff.get_font_charset(font_dir)

        for char in chars:
            if char in font_charsets:
                support.append(char)
            else:
                notSupport.append(char)

        if show_support:
            font_str = '\n'.join(support)
        else:
            font_str = '\n'.join(notSupport)

        with open('font.txt', 'w', encoding='utf-8') as f:
            f.write(font_str)

def preview(logger: Logger, config: str, output: str, font_dir: str, font_size: int):
    """
    生成字体预览图

    args:
        logger: 日志
        config: 生成配置文件名
        output: 生成的训练数据输出文件夹
        font_dir: 字体文件夹路径
        font_size: 预览字体大小
    """

    cfg = yaml.load(open(config, 'r', encoding='utf-8'), Loader=yaml.FullLoader)
    text = cfg['TEXT']['SAMPLE']['PREVIEW']

    print('prepare load font file')

    os.makedirs(output, exist_ok=True)

    tags = []
    whiteList = cfg['EFFECT']['FONTS']['white_list'] if 'white_list' in cfg['EFFECT']['FONTS'] else None
    ff = FontsFactory(logger, font_dir, whiteList = whiteList)
    fontUtil = FontUtil(cfg, logger)
    allFonts = ff.get_load_fonts()

    idx = 0
    tags.append(f'<h3>Preview font size {font_size}</h3>')

    for fn, fi in allFonts.items():
        try:
            idx += 1
            imgFn = f'{idx}.jpg'
            imgText = text + ' ' + fn
            font_file = fi[0]
            saveFile = os.path.join(output, imgFn)
            _, img = fontUtil.renderText(imgText, fn, font_file, font_size, True)
            cv2.imwrite(saveFile, img)

            tags.append(f'<img src="{imgFn}" alt="{html.escape(fn)}" title="{html.escape(fn)}" />')
        except Exception as e:
            logger.info(e)
            traceback.print_exc()

    generateImagePreviews(os.path.join(output, 'preview.html'), tags, '<br />')

    print('create font preview done!')


def rec(logger: Logger, config: str, output: str, font_dir: str, category: str, index_start: int):
    """
    生成 OCR 识别模型数据

    args:
        config: 生成配置文件名
        output: 生成的训练数据输出文件夹
        font_dir: 字体文件夹路径
        category: 生成的训练数据类别
        index_start: 图片文件名序号起始值
    """

    cfg = yaml.load(open(config, 'r', encoding='utf-8'), Loader=yaml.FullLoader)

    if font_dir is not None and font_dir != '':
        cfg['EFFECT']['FONTS']['fonts_dir'] = font_dir

    # 合成
    pipeline = Pipeline(cfg, logger, output, category, seq = index_start, display_interval=2000)
    pipeline.run()


def get_logger(log_save_path):
    """初始化日志"""

    kwargs = {'when': 'D',
            'interval': 1,
            'backupCount': 10,
            'console': True,  # 是否输出到屏幕
            'level': Logger.INFO,  # 日志level
            }

    return Logger('synth', log_save_path, **kwargs)

if __name__ == '__main__':
    args = parse_args()

    if os.path.isabs(args.config_file):
        cfg_file = args.config_file
    else:
        cfg_file = os.path.join(APP_PATH, 'configs/' + args.config_file)
    if not os.path.exists(cfg_file):
        print('config file not found: %s', cfg_file)
        os._exit(1)

    if args.output is None or '' == args.output:
        if args.entry in ['rec', 'det']:
            today = datetime.datetime.now().strftime('_%Y%m%d%H%M%S')
            fname = os.path.splitext(os.path.basename(args.config_file))[0]
            args.output = os.path.join(APP_PATH, 'output', args.entry, fname + today)
        else:
            args.output = os.path.join(APP_PATH, 'output', args.entry)

    obj_logger = get_logger(args.output)

    if 'rec' == args.entry:
        rec(obj_logger, cfg_file, args.output, args.font_dir, args.category, args.index_start)
    elif 'preview' == args.entry:
        preview(obj_logger, cfg_file, args.output, args.font_dir, args.font_size)
    elif 'check' == args.entry:
        check(obj_logger, cfg_file, args.font_dir, args.show_support, args.clean)
    elif 'stat' == args.entry:
        stat_vocab(obj_logger, cfg_file, args.font_dir)
    else:
        obj_logger.error('unknown entry: %s', args.entry)
