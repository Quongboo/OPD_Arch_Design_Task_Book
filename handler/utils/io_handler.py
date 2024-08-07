"""
    该PY文件实现读写相关的操作计算
"""

import json
import os


def read_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        json_data = file.read()
    content = json.loads(json_data)
    return content


def write_json(content: object, file: str):
    with open(file, "w",  encoding='utf-8') as f:
        json.dump(content, f)



def mkdir(path: str):
    """
    :param path:    待创建文件路径
    :return:
    """
    os.makedirs(path, exist_ok=True)

