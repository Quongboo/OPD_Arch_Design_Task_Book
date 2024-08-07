from math import ceil
"""
科室相关计算文件：
类型一：门诊科室患者人数相关计算
1、计算更新科室患者权重
2、计算普通科室患者人数分配
3、计算内外科混合科室患者人数分配
类型二：门诊科室房间数量、面积相关计算
4、计算科室中的诊室数量
5、计算医院诊室总体数量
6、计算需要参与房间计算的科室：排除内外代理科室
7、计算没有诊室字段的科室
8、配置科室房间数
9、过滤科室必要房间列表
10、计算科室房间面积
11、计算科室交通面积
12、计算科室必要面积
"""


"""
门诊科室患者人数相关计算
"""


def cal_weight_for_department_patient(department_list):
    """
    根据科室类型，计算需要患者人数分配的科室的patient_weight，并将更新后的权重重新写入科室之中
    :param department_list:科室列表
    :return:
    """
    # 初始化权重

    separate_medical_type_total_weight = 0.  # 单独的内科科室
    separate_surgery_type_total_weight = 0.  # 单独的外科科室
    single_specialty_type_total_weight = 0.  # 简单专科科室
    specialty_mix_type_total_weight = 0.  # 专科混合科室
    medical_mix_surgery_type_total_weight = 0.  # 内外科混合科室

    for department in department_list:
        type_name = department.get_type_class_name()
        patient_weight = department.get_patient_weight()
        if type_name == "single_type":
            continue
        elif type_name == "separate_medical_type":
            separate_medical_type_total_weight += patient_weight
        elif type_name == "separate_surgery_type":
            separate_surgery_type_total_weight += patient_weight
        elif type_name == "single_specialty_type":
            single_specialty_type_total_weight += patient_weight
        elif type_name == " specialty_mix_type":
            specialty_mix_type_total_weight += patient_weight
        elif type_name == "medical_mix_surgery_type":
            medical_mix_surgery_type_total_weight += patient_weight

    # TODO:分母为0的情况--报错:应该不存在这一种情况

    for department in department_list:
        type_name = department.get_type_class_name()
        if type_name == "separate_medical_type":
            department.set_patient_weight(department.get_patient_weight() / separate_medical_type_total_weight)
        elif type_name == "separate_surgery_type":
            department.set_patient_weight(department.get_patient_weight() / separate_surgery_type_total_weight)
        elif type_name == "single_specialty_type":
            department.set_patient_weight(department.get_patient_weight() / single_specialty_type_total_weight)
        elif type_name == " specialty_mix_type":
            department.set_patient_weight(department.get_patient_weight() / specialty_mix_type_total_weight)
        elif type_name == "medical_mix_surgery_type":
            department.set_patient_weight(department.get_patient_weight() / medical_mix_surgery_type_total_weight)


def cal_department_patient_nums(department_list, standard_proxy):
    """
    计算各科的患者人数：计算普通科室患者人数分配
    :param department_list: 科室列表
    :param standard_proxy: 国家标准计算方式代理
    :return:
    """
    for department in department_list:
        type_name = department.get_type_class_name()
        if type_name == "single_type":
            patient_nums = standard_proxy.query_class_value(department.get_standard_class_name())
            department.set_patient_nums(patient_nums)
            print(f"{department.get_name()}的患者人数为：{patient_nums}")
        elif type_name == "separate_medical_type":
            class_nums = standard_proxy.query_class_value(department.get_standard_class_name())
            patient_nums = ceil(class_nums * department.get_patient_weight())
            department.set_patient_nums(patient_nums)
            print(f"{department.get_name()}的患者人数为：{patient_nums}")
        elif type_name == "separate_surgery_type":
            class_nums = standard_proxy.query_class_value(department.get_standard_class_name())
            patient_nums = ceil(class_nums * department.get_patient_weight())
            department.set_patient_nums(patient_nums)
            print(f"{department.get_name()}的患者人数为：{patient_nums}")
        elif type_name == "single_specialty_type":
            class_nums = standard_proxy.query_class_value(department.get_standard_class_name())
            patient_nums = ceil(class_nums * department.get_patient_weight())
            department.set_patient_nums(patient_nums)
            print(f"{department.get_name()}的患者人数为：{patient_nums}")
        elif type_name == "specialty_mix_type":
            class_nums = standard_proxy.query_class_value(department.get_standard_class_name())
            patient_nums = ceil(class_nums * department.get_patient_weight())
            department.set_patient_nums(patient_nums)
            print(f"{department.get_name()}的患者人数为：{patient_nums}")


def cal_medical_mix_surgery_department_patient_nums(department_list):
    """
    计算内外科混合科室患者人数分配
    :param department_list: 科室列表
    :return:
    """

    surgery_mix_patient_nums = 0
    medical_mix_patient_nums = 0
    for department in department_list:
        if department.get_name() == "surgery_mix_proxy":
            surgery_mix_patient_nums = department.get_patient_nums()
        elif department.get_name() == "medical_mix_proxy":
            medical_mix_patient_nums = department.get_patient_nums()
    mix_patient_total_nums = surgery_mix_patient_nums + medical_mix_patient_nums
    print(f"内外混合科室总人数为：{mix_patient_total_nums}")

    for department in department_list:
        type_name = department.get_type_class_name()
        if type_name == "medical_mix_surgery_type":
            patient_nums = ceil(mix_patient_total_nums * department.get_patient_weight())
            mix_weight_total = department.get_mix_inter_med_weight() + department.get_mix_outer_med_weight()
            inter_nums = ceil((patient_nums * department.get_mix_inter_med_weight()) / mix_weight_total)
            outer_nums = ceil((patient_nums * department.get_mix_outer_med_weight()) / mix_weight_total)
            patient_nums_final = inter_nums + outer_nums
            department.set_patient_nums(patient_nums_final)
            print(f"{department.get_name()}的患者总人数为：{patient_nums_final}，"
                  f"内科患者人数为：{inter_nums}，外科患者人数为{outer_nums}")


"""
门诊科室房间数量、面积相关计算
"""


def cal_department_examination_nums(department_list):
    """
    计算门诊科室中的诊室数量：诊室数量=科室患者人数 /（该科室每小时医生接待患者数量 * 每间诊室房间的医生人数）
    :param department_list:科室列表
    :return:
    """
    for department in department_list:
        if department.get_type_class_name() == "basic_type" or department.get_name() == "surgery_mix_proxy" or \
                department.get_name() == "medical_mix_proxy":

            print(f'当前科室为{department.get_name()}没有患者人数，无法计算门诊诊室数量')
        elif department.get_patient_nums() is not None:
            consulting_room_nums = department.get_patient_nums() / \
                                   (department.get_per_doctor_hour_reception() *
                                    department.get_doctor_nums_per_examination())
            consulting_room_nums = ceil(consulting_room_nums)
            department.set_consulting_room_nums(consulting_room_nums)
            print(f"{department.get_name()}科室诊室数为：{department.get_consulting_room_nums()}")
        else:
            print(f'{department.get_name()}科室数量计算有问题')


def cal_department_examination_total_nums(department_list):
    """
    计算医院门诊诊室总体数量
    :param department_list: 科室列表
    :return:
    """
    consulting_total_nums = 0
    for department in department_list:
        consulting_total_nums += department.get_consulting_room_nums()
    print(f'医院门诊诊室总体数量为{consulting_total_nums}')


def depart_cal_room_name_list(department_list):
    """
    需要参与计算房间数量的科室
    :param department_list: 科室列表
    :return:
    """
    department_room_name = []
    for department in department_list:
        department_room_name.append(department.get_name())
    # 删除代理门诊房间
    department_room_name.remove('surgery_mix_proxy')
    department_room_name.remove('medical_mix_proxy')
    print(f"参与房间数量计算的科室有：{len(department_room_name)}个，为{department_room_name}")


def cal_department_none_examination(department_list):
    """
    计算哪些科室没有诊室：检查是否有科室忘记计算诊室数量
    :param department_list:科室列表
    :return:
    """
    # 检查哪些科室没有诊室
    depart_have_examination = []
    for department in department_list:
        department_room_list = department.get_room_config_list()
        for room in department_room_list.get_room_list():
            if room.get_name() == "examination":
                depart_have_examination.append(department.get_name())
    for department in department_list:
        if department.get_name() not in depart_have_examination:
            print(f'科室{department.get_name()}中没有诊室字段')


def cal_department_room_count(department_list):
    """
    配置科室房间数；将最小房间设置数量加入科室房间数-->将计算得出的诊室数量加入房间数
    :param department_list: 科室列表
    :return:
    """
    for department in department_list:
        # 将本科室最小房间数量遍历一遍，先添加到基础保底房间列表
        department_room_list = department.get_room_config_list()
        # 初始化房间数量
        for room in department_room_list.get_room_list():
            # 初始化room的数量是否为0
            room.set_count(int(0))
            # 将科室必要房间数量的加到房间数量之中
            room_min_count = int(room.get_min_count())
            room.set_count(room_min_count)

        # 将诊室的计算数量加到房间的数量之中
        for room in department_room_list.get_room_list():
            if room.get_name() == "examination":
                depart_consulting_nums = department.get_consulting_room_nums()
                room.set_count(int(depart_consulting_nums))
                print(f"当前科室{department.get_name()}存在诊室{depart_consulting_nums}间")


def cal_department_necessary_room(department_list):
    """
    过滤出科室的必要房间列表
    :param department_list: 科室列表
    :return:
    """
    for department in department_list:
        department_room_list = department.get_room_config_list()
        necessary_room_list = []
        for room in department_room_list.get_room_list():
            # print(room.get_count())
            if room.get_count() > 0:
                necessary_room_list.append(room)
        department.set_necessary_room_list(necessary_room_list)
        # print(f'{department.get_name()}中必要的科室有{len(necessary_room_list)}个，为：{necessary_room_list}')


def cal_department_necessary_area_from_room(department_list):
    """
    计算科室诊室及功能用房部分面积
    :param department_list:科室列表
    :return:
    """
    for department in department_list:
        necessary_room_list = department.get_necessary_room_list()
        total_necessary_area = 0
        for room in necessary_room_list:
            room_count = room.get_count()
            area = float(room.get_area()) * int(room_count)
            total_necessary_area += area
        department.set_depart_necessary_area_from_room(total_necessary_area)
        print(f'{department.get_name()}的房间必要面积为{department.get_depart_necessary_area_from_room()}')


def cal_department_necessary_traffic_area(department_list):
    """
    计算科室的必要交通面积：默认一个走廊，房间向两边排布
    :param department_list: 科室列表
    :return:
    """
    for department in department_list:
        corridor_width = department.get_corridor_width()
        necessary_room_list = department.get_necessary_room_list()
        total_width = 0
        for room in necessary_room_list:
            room_count = room.get_count()
            room_width = room.get_width()
            total_width += float(room_width) * int(room_count)
        total_necessary_traffic_area = total_width * corridor_width / 2
        department.set_total_necessary_traffic_area(total_necessary_traffic_area)
        print(f'{department.get_name()}的必要交通面积为{total_necessary_traffic_area}，走廊宽度设置为{corridor_width}')


def cal_department_necessary_total_area(department_list):
    """
    计算科室必要面积 = 必要房间面积+必要的交通面积
    :param department_list: 科室列表
    :return:
    """

    for department in department_list:
        necessary_total_area = department.get_total_necessary_traffic_area() + \
                               department.get_depart_necessary_area_from_room()
        department.set_necessary_total_area(necessary_total_area)
        # print(f'{department.get_name()}的必要面积为{necessary_total_area}')
