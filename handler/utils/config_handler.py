"""
处理上传的配置文件的相关函数
"""

"""
将修改配置的department文件写为json或将json写为方便修改的csv文件
1、depart_json_to_csv-->将科室json文件写为csv文件
2、depart_csv_to_json-->将科室csv文件写为json文件
3、
"""
import csv
import json


def depart_json_to_csv(json_file, csv_file):
    """
    json-->csv
    :param json_file:
    :param csv_file:
    :return:
    """
    # 读取 JSON 文件
    with open(json_file, 'r') as f:
        data = json.load(f)

    # 提取 JSON 数据中的键（假设所有对象具有相同的键）
    keys = data[0].keys()

    # 写入 CSV 文件
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)

        writer.writeheader()  # 写入 CSV 文件的标题行

        for row in data:
            writer.writerow(row)  # 逐行写入数据

    print("转换完成！")


def depart_csv_to_json(csv_file, json_file):
    """
    csv-->json
    :param csv_file:
    :param json_file:
    :return:
    """
    # 读取 CSV 文件
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        data = [dict(row) for row in reader]

    # 将空字段转换为 None，将数字字段转换为对应的数值类型
    for row in data:
        for key, value in row.items():
            if value == '':
                row[key] = None
            else:
                try:
                    # 尝试将字段值转换为整数
                    row[key] = int(value)
                except ValueError:
                    try:
                        # 尝试将字段值转换为浮点数
                        row[key] = float(value)
                    except ValueError:
                        # 字段值不是数字，保持原样
                        pass

    # 写入 JSON 文件
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4, default=serialize)

    print("转换完成！")


def serialize(obj):
    """
    自定义序列化方法，将数字字段以数值类型写入 JSON
    :param obj:
    :return:
    """
    if isinstance(obj, (int, float)):
        return obj
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


import zipfile
import os

def zip_folder(folder_path, output_path):
    """
    文件夹压缩
    :param folder_path: 待压缩文件夹地址
    :param output_path: 输出文件地址
    :return:
    """
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))


def unzip_file(zip_file_path, output_folder_path):
    """
    压缩文件解压
    :param zip_file_path: 压缩文件地址
    :param output_folder_path: 解压后文件夹地址
    :return:
    """
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder_path)


"""
将room的所有csv配置文件写为一个json文件，代替之前的写法，便于之后进行文件修改时使用
"""
import csv
import json
import os
import shutil

def read_csv(filename):
    """
    读取csv的函数-->list
    :param filename: csv的文件名称
    :return: list
    """
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        csv_list = []
        for row in reader:
            csv_list.append(row)
        return csv_list


def write_json(room_list, filename):
    # 将列表写入JSON文件
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(room_list, file, ensure_ascii=False)

def delete_null_line(input_file, output_file):
    """
    删除csv文件中的空行
    :param input_file: csv文件（存在空行）
    :param output_file: csv文件（没有空行）
    :return:
    """
    with open(input_file, "r", newline="", encoding='utf-8') as file_in, open(output_file, "w", newline="",
                                                                              encoding='utf-8') as file_out:
        reader = csv.reader(file_in)
        writer = csv.writer(file_out)

        for row in reader:
            if any(field.strip() for field in row):  # 检查行中是否有非空字段
                writer.writerow(row)

def read_csv_filename(floder_path):
    """
    读取一个文件夹中的所有文件返回一个文件名列表
    # TODO: 只读取csv文件
    :param floder_path: 文件夹名称
    :return: list
    """
    file_list = []
    for root, dirs, files in os.walk(floder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return file_list

# 从文件夹中读取所有的json
def read_folder_all_json_files(folder_path):
    """
    读取一个文件夹内的所有json文件
    :param folder_path: 文件夹名称
    :return: json-->字典
    """
    data = {}

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.json') and os.path.isfile(file_path):
            # 读取JSON文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            # 将JSON数据添加到字典中
            data[filename] = json_data
    return data

def csv_to_dict(csv_list: list):
    """
    将一个指定格式的list文件解析为一个字典
    :param csv_list: 源于csv的list
    :return:
    """
    department_name = csv_list[0][0]
    room_list = []
    for room in csv_list:
        if room[2] is not None:
            room_dict = {
                "name": room[2],
                "desc": room[4],

                "count": room[5],
                "area": room[6],
                "width": room[7],
                "length": room[8],
                "height": room[9],

                "room_type": room[10],
                "floor": room[11],
                "doctor_num": room[12],

                "access_weight": room[13],
                "layout_weight": room[14],
                "windows_weight": room[15],

                "min_area": room[16],
                "max_area": room[17],

                "min_count": room[18],
                "max_count": room[19],
            }
            room_list.append(room_dict)
    room_list = room_list[1:]
    department_dict = {department_name: room_list}
    return department_dict, department_name


def room_csv_to_json(raw_csv_file_path: str,
                     save_file: str,
                     room_config_name: str):
    """
    读取文件夹中的所有csv文件，写成一个json文件
    1、删除csv文件中的空行-->储存到中间路径
    2、将csv文件写成json文件
    3、将单一的json文件整合为一个完整的json文件

    :param raw_csv_file_path: 包含所有待处理的csv文件夹地址
    :param save_file: 文件储存地址
    :param room_config_name: room_config的命名
    :return:
    """
    # 删除csv文件中的空行

    csv_name_list = read_csv_filename(raw_csv_file_path)
    without_null_line_path = os.path.join(save_file, "room_csv_without_null_line")
    if os.path.exists(without_null_line_path):
        shutil.rmtree(without_null_line_path)
    os.makedirs(without_null_line_path)
    for file in csv_name_list:
        raw_file = file
        out_name = os.path.split(file)[-1]
        fin_file = os.path.join(without_null_line_path, out_name)
        delete_null_line(raw_file, fin_file)

    # 写为json文件
    without_null_line_csv = os.path.join(save_file, "room_csv_without_null_line")
    single_json_file_path = os.path.join(save_file, "department_room_json")
    if os.path.exists(single_json_file_path):
        shutil.rmtree(single_json_file_path)
    os.makedirs(single_json_file_path)
    without_null_line_list = read_csv_filename(without_null_line_csv)
    for csv_file in without_null_line_list:
        depart_list = ["gynecology", "obstetrics", "pediatrics", "tcm", "endocrine", "hematology",
                       "immuno_rheumatology",
                       "infectious", "medical_mix_proxy", "general_sugery", "orthopedic", "surgery_mix_proxy",
                       "cardiovascular_center",
                       "respiratory_center", "digestive_center", "neurocerebrovascular_center", "tumor_center",
                       "urology_nephrology_center",
                       "stomatology", "dermatology", "physiotherapy", "aesthetic", "counseling", "ophthalmology", "ent",
                       "operating",
                       "opd_hall", "opd_pharmacy", "opd_assay", "opd_treatment_room", "opd_office"]
        csv_list = read_csv(csv_file)

        if csv_list[0][0] in depart_list:
            department_dict, department_name = csv_to_dict(csv_list)
            save_file_name = os.path.join(single_json_file_path, f"{department_name}_room.json")
            write_json(department_dict, save_file_name)
        else:
            print(f'{csv_list[0][0]}不在科室列表中')

    # 将多个json文件合并为一个json文件
    json_folder_path = os.path.join(save_file, "department_room_json")
    json_data_dict = read_folder_all_json_files(json_folder_path)
    room_dict = {}
    for filename, json_data in json_data_dict.items():
        room_dict.update(json_data)
    save_room_config_path = os.path.join(save_file, f"{room_config_name}.json")
    write_json(room_dict, save_room_config_path)

    print('房间配置文件已从csv转化为json')

