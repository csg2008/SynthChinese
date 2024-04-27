# -*- coding:utf-8 -*-
"""
@author zhangjian
"""

import os
import cv2
import random

class bgFactory:
    """背景图工厂"""

    def __init__(self, cfg):
        self.cfg = cfg
        self.all_bgs = self.get_bgs()
        self.bgs_keys = list(self.all_bgs.keys())

    def get_bgs(self):
        all_imgs = {}
        bgs_dir = self.cfg['DIR']
        allow_images = ['.jpg', '.jpeg', '.png']
        white_list = self.cfg['white_list'] if 'white_list' in self.cfg else None

        if os.path.exists(bgs_dir):
            all_files = os.listdir(bgs_dir)

            if white_list and len(white_list) > 0:
                pic_files = list(filter(lambda x: os.path.splitext(x)[1] in allow_images and x in white_list, all_files))
            else:
                pic_files = list(filter(lambda x: os.path.splitext(x)[1] in allow_images, all_files))

            for fname in pic_files:
                bg = cv2.imread(os.path.join(bgs_dir, fname))
                bg_name = os.path.splitext(fname)[0].replace('_', '')
                all_imgs[bg_name] = bg

        return all_imgs

    def generate_bg(self, height: int = None, width: int = None):
        if height is None or width is None:
            height = self.cfg['SIZE'][0]
            width = self.cfg['SIZE'][1]
        bg_name = random.choice(self.bgs_keys)
        bg_img = self.all_bgs[bg_name]
        # check shape and resize
        h, w = bg_img.shape[0:2]
        if w < width or h < height:
            w1, h1 = int(w * height / h), height
            w2, h2 = width, int(h * width / w)
            if w1 >= width and h1 >= width:
                bg_img = cv2.resize(bg_img, (w1, h1), interpolation=cv2.INTER_AREA)
            else:
                bg_img = cv2.resize(bg_img, (w2, h2), interpolation=cv2.INTER_AREA)
        # random crop
        h, w = bg_img.shape[0:2]
        x = random.randint(0, w - width)
        y = random.randint(0, h - height)
        cropped_img = bg_img[y:y + height, x:x + width, :]

        return bg_name, cropped_img

    def play(self, FPS=5):
        while True:
            bg_name, bg_img = self.generate_bg()
            cv2.imshow('Play', bg_img)
            key = cv2.waitKey(int(1000/FPS))
            if key == ord('q'):
                break
        cv2.destroyAllWindows()


if __name__ == '__main__':
    bgf = bgFactory('../../data/background')
    # bgf.play()
    cv2.imshow('test', bgf.all_bgs['bg2'])
    _,img2 = bgf.generate_bg()
    cv2.imshow('test1', img2)

