import os
from handler.utils.io_handler import mkdir, write_json


def get_cached_path(hospital_name: str, cached_dir):
    """
    :param hospital_name: 医院名称
    :return: 创建的文件路径名称
    """
    path = os.path.join(cached_dir, hospital_name)
    mkdir(path)

    return path


def save_brief_json_file(cached_dir, hospital):
    """
    将医院任务书文件保存为一个json
    :param cached_dir: 中间文件缓存路径
    :param hospital: 实例的医院
    :return:
    """
    hospital_brief_json_data = hospital.to_json()
    hospital_name = hospital.get_name()
    save_path = get_cached_path(hospital_name, cached_dir)
    file_path = os.path.join(save_path, f'{hospital.get_name()}_brief.json')
    write_json(hospital_brief_json_data, file_path)
    print(f'医院{hospital_name}任务书--json保存成功：{file_path}')


def save_brief_csv_file(cached_dir, hospital):
    """
    将医院任务书文件保存为四个csv文件
    :param cached_dir: 中间文件缓存路径
    :param hospital: 实例的医院
    :return:
    """
    hospital_name = hospital.get_name()
    save_path = get_cached_path(hospital_name, cached_dir)
    # 储存医院csv文件
    hospital_csv_path = os.path.join(save_path, f'{hospital.get_name()}_hospital_brief.csv')
    hospital.write_csv_hospital(hospital_csv_path)
    # 储存门诊csv文件
    outpatient_csv_path = os.path.join(save_path, f'{hospital.get_name()}_outpatient_brief.csv')
    outpatient_proxy = hospital.outpatient_config.get_outpatient_list()[0]
    outpatient_proxy.write_csv_outpatient(outpatient_csv_path)
    # 储存科室csv文件
    department_csv_path = os.path.join(save_path, f'{hospital.get_name()}_department_brief.csv')
    department_proxy = hospital.outpatient_config.get_outpatient_list()[0].department_list
    department_proxy.write_csv_department(department_csv_path)
    # 储存房间csv文件
    room_csv_path = os.path.join(os.path.join(save_path, f'{hospital.get_name()}_room_brief.csv'))
    department_proxy = hospital.outpatient_config.get_outpatient_list()[0].department_list
    department_proxy.write_csv_depart_room(room_csv_path)
