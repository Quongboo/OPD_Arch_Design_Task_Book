import os
from entity.hospital import HospitalEntity
from handler.utils.io_handler import write_json, read_json
from cached.cached_commander import save_brief_json_file, save_brief_csv_file



def generate_outpatient_brief(name, need_bed_nums, need_service_people_nums,
                              need_patient_nums, outpatient_land_area,
                              depart_config_json_file, room_config_json_file,
                              required_depart_list,
                              residual_area_method, residual_area_method2_config):
    """
    医院门诊任务书生成入口函数
    :param name:                            医院名称
    :param need_bed_nums:                   医院床位数
    :param need_service_people_nums:        医院服务人口数
    :param need_patient_nums:               医院患者人数
    :param outpatient_land_area:            门诊占地面积
    :param depart_config_json_file:         科室配置文件
    :param room_config_json_file:           房间配置文件
    :param required_depart_list:            科室需求表
    :param residual_area_method:            剩余面积分配策略
    :param residual_area_method2_config:    剩余面积分配策略2配置文件
    :return:
    """
    # 配置基础文件
    department_element = read_json(depart_config_json_file)
    outpatient_element = [{
        "land_area": outpatient_land_area,
        "department_list": department_element
    }]

    file_path = f'data_cached/{name}'
    os.makedirs(file_path, exist_ok=True)
    save_outpatient_element_json_path = os.path.join(file_path, f'{name}_outpatient_element.json')
    write_json(outpatient_element, save_outpatient_element_json_path)

    # 配置文件
    element = {

        "name": str(name),
        "need_bed_nums": int(need_bed_nums),
        "need_service_people_nums": int(need_service_people_nums),
        "need_patient_nums": need_patient_nums,
        "required_depart_list": required_depart_list,
        "serialize_outpatient_file": save_outpatient_element_json_path,
        "serialize_room_file": room_config_json_file,
        "residual_area_method2_config": residual_area_method2_config,
        "residual_area_method": residual_area_method
    }

    # 实例化医院对象
    hospital = HospitalEntity.from_json(element)
    # 医院任务书设计阶段
    hospital.design_brief()
    # 储存任务书生成的中间路径
    cached_dir = "data_cached"
    # 储存json文件-->一个文件
    save_brief_json_file(cached_dir, hospital)
    # 储存csv文件-->医院、门诊、科室、科室-房间四个csv
    save_brief_csv_file(cached_dir, hospital)


def generate_outpatient_brief_webui(name, need_bed_nums, need_service_people_nums, need_patient_nums,
                                    outpatient_land_area, depart_config_swap, room_config_swap, area_config_swap,
                                    check_required_depart, method2_config):
    """
    使用webui的入口函数

    :param name:                            医院名称
    :param need_bed_nums:                   医院床位数
    :param need_service_people_nums:        医院服务片区人数
    :param need_patient_nums:               医院患者数
    :param outpatient_land_area:            门诊占地面积
    :param depart_config_swap:              科室配置文件
    :param room_config_swap:                房间配置文件
    :param area_config_swap:                剩余面积分配模式
    :param check_required_depart:           需求科室配置文件
    :param method2_config:                  输入的剩余分配--2模式值
    :return:
    """

    # 判断用户选择哪个科室配置文件
    print(depart_config_swap)
    if depart_config_swap == "department_v3":
        print('使用基础提供的科室配置文件')
        depart_config_json_file = os.path.join('configs', f"{depart_config_swap}.json")
    else:
        print('使用用户提供的科室配置文件')
        depart_config_json_file = os.path.join(f'configs/user/{depart_config_swap}', f"{depart_config_swap}.json")

    # 判断用户使用哪个房间配置文件
    if room_config_swap == "room_v3":
        print('使用基础提供的房间配置文件')
        room_config_json_file = os.path.join('configs', f"{room_config_swap}.json")
    else:
        print('使用用户提供的房间配置文件')
        room_config_json_file = os.path.join(f'configs/user/{room_config_swap}', f"room_{room_config_swap}.json")


    # 配置必须选项-->内外科室代理
    medical_mix_proxy = 'medical_mix_proxy'
    surgery_mix_proxy = 'surgery_mix_proxy'
    check_required_depart.append(medical_mix_proxy)
    check_required_depart.append(surgery_mix_proxy)
    required_depart_list = check_required_depart

    # 判断用户选择那种选取剩余面积分配模式:策略一：自动化增加房间数量；策略二：根据配置增加房间配置
    if area_config_swap == "method1":
        residual_area_method = 'method1'
    elif area_config_swap == "method2":
        residual_area_method = 'method2'
        # 替换用户输入的method2_config/解析字符串
        import json
        if method2_config is not None or "":
            print(method2_config)
            print("用户输入的method2_config")
            method2_config = json.loads(method2_config)

    else:
        residual_area_method = ""

    # 配置策略2指标:如果有剩余面积，优先增加哪些部分
    # residual_area_method2_config = {
    #     "input_depart_room_name_add_area": ["aesthetic/cryotherapy_room/20", "depart/room/area"],
    #     "input_depart_room_nums_add_count": ["aesthetic/cryotherapy_room/5", "depart/room/3"],
    #     "input_depart_corridor_width": ["aesthetic/3.3", "depart/3"]}

    # 配置基础文件
    department_element = read_json(depart_config_json_file)
    outpatient_element = [{
        "land_area": float(outpatient_land_area),
        "department_list": department_element
    }]


    file_path = f'data_cached/{name}'
    os.makedirs(file_path, exist_ok=True)
    save_outpatient_element_json_path = os.path.join(file_path, f'{name}_outpatient_element.json')
    write_json(outpatient_element, save_outpatient_element_json_path)

    # 配置文件
    element = {

        "name": str(name),
        "need_bed_nums": int(need_bed_nums),
        "need_service_people_nums": int(need_service_people_nums),
        "need_patient_nums": need_patient_nums,
        "required_depart_list": required_depart_list,
        "serialize_outpatient_file": save_outpatient_element_json_path,
        "serialize_room_file": room_config_json_file,
        "residual_area_method2_config": method2_config,
        "residual_area_method": residual_area_method
    }

    # 实例化医院对象
    hospital = HospitalEntity.from_json(element)
    # 医院任务书设计阶段
    hospital.design_brief()
    # 储存任务书生成的中间路径
    cached_dir = "data_cached"
    # 储存json文件-->一个文件
    save_brief_json_file(cached_dir, hospital)
    # 储存csv文件-->医院、门诊、科室、科室-房间四个csv
    save_brief_csv_file(cached_dir, hospital)


# if __name__ == "__main__":
#
#     name = 'qqq'
#     need_bed_nums = '600'
#     need_service_people_nums = '18000'
#     need_patient_nums = '1000'
#     outpatient_land_area = int(6000)
#
#     depart_config_json_file = 'configs/department_v3.json'
#     room_config_json_file = 'configs/room_v3.json'
#
#     required_depart_list = ["gynecology", "obstetrics", "pediatrics", "tcm", "endocrine", "hematology",
#                                  "immuno_rheumatology",
#                                  "infectious", "medical_mix_proxy", "general_sugery", "orthopedic", "surgery_mix_proxy",
#                                  "cardiovascular_center",
#                                  "respiratory_center", "digestive_center", "neurocerebrovascular_center",
#                                  "tumor_center",
#                                  "urology_nephrology_center",
#                                  "stomatology", "dermatology", "physiotherapy", "aesthetic", "counseling",
#                                  "ophthalmology",
#                                  "ent", "operating",
#                                  "opd_hall", "opd_pharmacy", "opd_assay", "opd_treatment_room", "opd_office"]
#
#     # 选取分配剩余部分面积方式：策略一：自动化增加房间数量；策略二：根据配置增加房间配置
#     residual_area_method = 'method1'
#     # 配置策略2指标:如果有剩余面积，优先增加哪些部分
#     residual_area_method2_config = {
#         "input_depart_room_name_add_area": ["aesthetic/cryotherapy_room/20", "depart/room/area"],
#         "input_depart_room_nums_add_count": ["aesthetic/cryotherapy_room/5", "depart/room/3"],
#         "input_depart_corridor_width": ["aesthetic/3.3", "depart/3"]}
#
#     generate_outpatient_brief(name, need_bed_nums, need_service_people_nums,
#                               need_patient_nums, outpatient_land_area,
#                               depart_config_json_file, room_config_json_file,
#                               required_depart_list,
#                               residual_area_method, residual_area_method2_config)
