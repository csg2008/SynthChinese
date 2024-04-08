from collections import Counter
from typing import List

def read_charset(charset_fp):
    alphabet = []
    with open(charset_fp, encoding='utf-8') as fp:
        for line in fp:
            alphabet.append(line.rstrip('\n'))
    inv_alpha_dict = {_char: idx for idx, _char in enumerate(alphabet)}
    if len(alphabet) != len(inv_alpha_dict):
        repeated = Counter(alphabet).most_common(len(alphabet) - len(inv_alpha_dict))
        raise ValueError(f'repeated chars in vocab: {repeated}')

    return alphabet, inv_alpha_dict

def generateImagePreviews(saveFile: str, tags: List[str], sep: str = '') -> None:
    """
    生成图片预览文件
    Args:
        saveFile 预览文件路径
        tags 图片标签列表
    """
    with open(saveFile, 'w', encoding='utf-8') as f:
        f.write('<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title>Preview</title></head><body>')
        f.write(sep.join(tags))
        f.write('</body></html>')