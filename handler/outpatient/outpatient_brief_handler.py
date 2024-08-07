import math

"""
门诊楼相关计算文件：
1、计算/读取门诊土地占地面积（未完成）
2、计算医院门诊建筑面积最大/最小值
3、计算医院门诊楼预估层数
4、计算医院门诊日均门诊量
5、计算医院门诊必要面积
6、计算医院门诊可增加面积
7、计算医院门诊公共部分交通面积增加值
8、计算门诊剩余面积分配策略一：增加layout_weight大的房间数量
9、计算门诊剩余面积分配策略二：根据输入需求增加面积
10、将科室面积写入科室总面积
11、计算门诊楼层数
"""


def cal_outpatient_land_area():
    # TODO:读取门诊楼占地面积
    return 0.


def cal_outpatient_max_build_area(hospital_area):
    """
    :param hospital_area: 医院建筑面积
    :return: 计算门诊建筑面积最大值
    """
    max_multi = 0.15
    return max_multi * hospital_area


def cal_outpatient_min_build_area(hospital_area):
    """
    :param hospital_area: 医院建筑面积
    :return: 计算门诊建筑面积最小值
    """
    min_multi = 0.12
    return min_multi * hospital_area


def cal_outpatient_floor_num(land_area: float,
                             max_build_area: float
                             ):
    """
    :param land_area:      门诊楼面积
    :param max_build_area: 最大建筑面积
    :return:               门诊楼预估层数
    """
    land_area = float(land_area)
    max_build_area = float(max_build_area)
    return math.ceil(max_build_area / land_area)


def cal_range_use_min_and_max(true_value: int,
                              min_weight: float,
                              max_float: float):
    """
    支持cal_outpatient_daily_paitent_nums计算
    :param true_value:  服务人数
    :param min_weight:  最小值权重
    :param max_float:   最大值权重
    :return:最小值、最大值
    """
    return true_value * min_weight, true_value * max_float


def cal_outpatient_daily_patient_nums(service_people_nums: int,
                                      need_bed_nums: int
                                      ):
    """
    根据医院床位数及片区服务人口数计算医院日均门诊量
    :param service_people_nums: 医院片区服务人数
    :param need_bed_nums: 医院床位数
    :return: 医院门诊日均患者数
    """
    service_min_nums, service_max_nums = cal_range_use_min_and_max(service_people_nums,
                                                                   7 / 250, 10 / 250
                                                                   )
    bed_min_nums, bed_max_nums = cal_range_use_min_and_max(need_bed_nums,
                                                           1.5, 3)
    if service_min_nums < bed_max_nums < service_max_nums:
        return bed_max_nums
    elif bed_max_nums < service_min_nums:
        print('床位数偏小')
        return service_min_nums
    elif service_max_nums < bed_max_nums:
        print('床位数偏大')
        return service_max_nums
    else:
        print("相等")
        return bed_max_nums

def cal_outpaint_total_patient_nums(department_list):
    """
    计算由各个科室统计得到的医院门诊患者总人数
    :param department_list: 医院门诊科室列表
    :return: 医院门诊患者总人数
    """
    total_nums = 0
    for department in department_list:
        if department.get_patient_nums() is not None:
            patient_nums = department.get_patient_nums()
            total_nums += patient_nums
    # 减去代理
    for department in department_list:
        if department.get_name() == "surgery_mix_proxy":
            total_nums -= department.get_patient_nums()
        elif department.get_name() == "medical_mix_proxy":
            total_nums -= department.get_patient_nums()
    print(f"医院门诊患者总人数为{total_nums}")
    return total_nums


def cal_outpatient_area_necessary(department_list):
    """

    :param department_list：医院门诊科室列表
    :return: 医院门诊必要面积
    """
    opd_necessary_area = 0
    for department in department_list:
        if department.get_necessary_total_area() is not None:
            opd_necessary_area += float(department.get_necessary_total_area())
        else:
            print(f'{department.get_name()}科室的必要总面积值为None')
    print(f"医院门诊的必要面积为：{opd_necessary_area}")
    return opd_necessary_area


def cal_excess_outpatient_area(outpatient_area_necessary, input_design_build_area,
                               min_build_area, max_build_area):
    '''
    计算门诊楼可增加面积
    :param outpatient_area_necessary:   门诊部面积必要值
    :param input_design_build_area:     门诊部输入设计值
    :param min_build_area:              门诊部建筑最小值
    :param max_build_area:              门诊部建筑最大值
    :return:                            门诊部可增加面积
    '''
    area_difference = 0

    # 如果存在用户输入值，以用户输入值为准
    if input_design_build_area is not None:
        print(f'门诊部面积由用户输入，面积为：{input_design_build_area}')
        area_difference = input_design_build_area - outpatient_area_necessary
    else:
        # 如果门诊部建筑最小值大于必要值，返回其与最小值的差
        if min_build_area - outpatient_area_necessary > 0:
            area_difference = min_build_area - outpatient_area_necessary
        else:
            area_difference = max_build_area - outpatient_area_necessary
            if area_difference < 0:
                print(f'门诊面积的必要值大于门诊部建筑允许的最大值，门诊部建筑的必要值为{outpatient_area_necessary}，'
                      f'门诊部建筑允许的最大值为{max_build_area}')
                print(f'门诊面积为门诊必要面积')
                return 0
                # raise ValueError

    print(f'门诊部可用的余额面积为：{area_difference}')
    return area_difference


def cal_add_outpatient_public_traffic_area(excess_outpatient_area):
    """
    在多余的面积中增加交通面积的多少，默认:add_public_traffic_multi_weight = 0.2
    :param excess_outpatient_area: 剩余的门诊部面积
    :return: 增加的交通部分面积
    """
    add_public_traffic_multi_weight = 0.2
    add_public_traffic_area = excess_outpatient_area * add_public_traffic_multi_weight
    return add_public_traffic_area


def cal_excess_area_for_department(excess_outpatient_area, add_outpatient_traffic_area):
    """
    计算剩余面积中可分配给科室的面积
    :param excess_outpatient_area: 剩余的门诊部面积
    :param add_outpatient_traffic_area: 增加的门诊部交通面积
    :return: 可供科室分配的门诊部面积
    """
    outpatient_area_residual = excess_outpatient_area - add_outpatient_traffic_area
    print(f'可供门诊科室分配的面积为:{outpatient_area_residual}')
    return outpatient_area_residual


def cal_add_count_for_depart_room(outpatient_area_residual, depart_list):
    """
    门诊剩余面积分配策略一：增加layout_weight大的房间数量
    1、按照depart的layout_weight进行排序
    2、选择layout_weight较大的depart
    3、选择该depart中room的layout_weight最大的一个，将其数量+1
    4、如果该房间数量大于max_count,就选取下一个depart进行第3步操作
    5、结束条件是：没有可供分配的面积

    :param outpatient_area_residual: 门诊科室可分配的面积
    :param depart_list: 门诊持有的科室列表
    :return:
    """

    while outpatient_area_residual > 0:

        department_list = depart_list.get_department_list()

        sorted_layout_weight_depart_list = sorted(department_list,
                                                  key=lambda obj: obj.layout_weight, reverse=True)  # 按照layout_weight排序

        current_outpatient_area_residual = outpatient_area_residual                                 # 当前可供分配的面积
        print(f'当前剩余可供分配的面积为{current_outpatient_area_residual}')

        for depart in sorted_layout_weight_depart_list:

            room_list_entity = depart.get_room_config_list()
            room_list = room_list_entity.get_room_list()
            # depart的room_list
            if not room_list:
                continue
            else:
                max_layout_weight_room = max(room_list,
                                             key=lambda obj: obj.layout_weight).get_layout_weight()  # layout_weight最大的房
                max_room = [obj for obj in room_list if obj.layout_weight == max_layout_weight_room]  # 处理有同样大的情况
                for room in max_room:
                    if int(room.get_count()) < int(room.get_max_count()):                            # 判断是否达到最大数量
                        room_count = room.get_count()
                        if float(room.get_area()) < outpatient_area_residual:                        # 判断面积是否够添加
                            room.set_count(room_count + 1)
                            print(f'增加房间为{depart.get_name()}的{room.get_name()},增加后数量为{room.get_count()}')
                            outpatient_area_residual = \
                                float(outpatient_area_residual) - float(room.get_area())             # 剩余面积减去该部分面积
                            break
                    else:
                        print(f'{room.get_name()}房间已达到最大数量限制, 剩余可分配面积为{outpatient_area_residual}')

        if outpatient_area_residual == current_outpatient_area_residual:                            # 没有房间可增加面积
            break                                                                                   # 退出while
    print(f'增加房间数量后，剩余无法分配的面积为：{outpatient_area_residual}')


def cal_input_add_area_or_count_for_depart_room(outpatient_area_residual,
                                                depart_list,
                                                residual_area_method2_config: dict):
    """
    门诊剩余面积分配策略二：根据输入需求增加面积
    1、增加房间面积，遍历列表
    2、增加房间数量，遍历列表
    3、增加交通部分面积，遍历列表

    :param residual_area_method2_config: 策略二输入字典
    :param outpatient_area_residual: 门诊科室可分配的面积
    :param depart_list: 门诊持有的科室列表
    :return:
    """

    input_depart_room_name_add_area = residual_area_method2_config["input_depart_room_name_add_area"]
    input_depart_room_nums_add_count = residual_area_method2_config["input_depart_room_nums_add_count"]
    input_depart_corridor_width = residual_area_method2_config["input_depart_corridor_width"]
    """
    input_depart_room_name_add_area: （增加房间面积）输入名称和增加的面积：[部门/房间/面积，部门/房间/面积]
    nput_depart_room_nums_add_count: （增加房间数量）输入名称增加房间数量：[部门/房间/增加数量，部门/房间/增加数量]
    input_depart_corridor_width: (增加交通面积) 输入名称，增加部门交通廊道宽度；[部门/交通走廊宽度]
    """

    for department in depart_list.get_department_list():

        # TODO:名称输入错误的容错

        # 增加输入房间的面积
        if input_depart_room_name_add_area is not None:
            for add_area_input in input_depart_room_name_add_area:
                split_list = add_area_input.split("/")
                depart_name = split_list[0]
                room_name = split_list[1]
                add_area = split_list[2]

                if department.get_name() == depart_name:
                    for room in department.get_room_config_list().get_room_list():
                        if room.get_name() == room_name:
                            room_raw_area = float(room.get_area())
                            room_add_area = float(add_area)
                            if room_add_area + room_raw_area <= float(room.get_max_area()):  # 判断是否超出房间最大面积
                                add_total_area = room_add_area * int(room.get_count())
                                if outpatient_area_residual - add_total_area >= 0:  # 不超出剩余部分面积的情况
                                    room.set_area(room_raw_area + room_add_area)
                                    outpatient_area_residual -= add_total_area
                                    print(f'{depart_name}-{room_name}已增加面积至{room.get_area()}')

                                else:
                                    # TODO：超出了剩余部分面积，策略：尽可能的按照3的模数分配给这一个房间--检查
                                    # 每个房间允许增加的面积
                                    outpatient_area_residual = outpatient_area_residual  # 剩余部分面积
                                    room_count = int(room.get_count())  # 获取当前房间的数量
                                    each_room_add_area_raw = outpatient_area_residual / room_count  # 允许每个房间增加的面积原始值（每个房间允许分配的最大值）

                                    # 增加面宽，按照0.3m为模数
                                    room_width = room.get_width()  # 获取房间的宽度
                                    add_single_room_width_raw = each_room_add_area_raw / float(
                                        room.get_length())  # 每个房间可增加的最大的宽度
                                    add_single_room_width = math.floor(
                                        add_single_room_width_raw / 0.3) * 0.3  # 按照0.3的模数可增加的房间宽度
                                    new_room_width = float(room_width) + float(add_single_room_width)  # 更新的房间宽度
                                    if new_room_width > float(room.get_width()):  # 新的房间宽度大于原始房间宽度
                                        new_single_room_area = new_room_width * float(room.get_length())  # 更新的房间面积

                                        add_area_total = (new_single_room_area - float(room.get_area())) \
                                                         * int(room.get_count())  # 增加的总面积
                                        room.set_width(new_room_width)
                                        room.set_area(new_single_room_area)

                                        outpatient_area_residual -= add_area_total
                                    else:
                                        continue
                            else:  # 超出房间最大面积就设置为最大面积
                                add_room_area = float(room.get_max_area()) - float(room.get_area())
                                add_total_area = add_room_area * int(room.get_count())
                                if outpatient_area_residual - add_total_area > 0:
                                    room.set_area(float(room.get_max_area()))
                                    outpatient_area_residual -= add_room_area
                                    print(f'增加输入房间的面积超出该类型房间设定的最大面积，{room_name}允许的最大面积为：'
                                          f'{room.get_max_area()}，已将该房间设定为允许的最大面积')
                                else:
                                    # TODO：超出了剩余部分面积，策略：尽可能的按照3的模数分配给这一个房间--检查
                                    # 每个房间允许增加的面积
                                    outpatient_area_residual = outpatient_area_residual  # 剩余部分面积
                                    room_count = int(room.get_count())  # 获取当前房间的数量
                                    each_room_add_area_raw = outpatient_area_residual / room_count  # 允许每个房间增加的面积原始值（每个房间允许分配的最大值）

                                    # 增加面宽，按照0.3m为模数
                                    room_width = room.get_width()  # 获取房间的宽度
                                    add_single_room_width_raw = each_room_add_area_raw / float(
                                        room.get_length())  # 每个房间可增加的最大的宽度
                                    add_single_room_width = math.floor(
                                        add_single_room_width_raw / 0.3) * 0.3  # 按照0.3的模数可增加的房间宽度
                                    new_room_width = float(room_width) + float(add_single_room_width)  # 更新的房间宽度
                                    if new_room_width > float(room.get_width()):  # 新的房间宽度大于原始房间宽度
                                        new_single_room_area = new_room_width * float(room.get_length())  # 更新的房间面积

                                        add_area_total = (new_single_room_area - float(room.get_area())) \
                                                         * int(room.get_count())  # 增加的总面积
                                        room.set_width(new_room_width)
                                        room.set_area(new_single_room_area)

                                        outpatient_area_residual -= add_area_total
                                    else:
                                        continue
                        else:
                            continue
                else:
                    continue

        # 增加输入房间的数量
        # input_depart_room_nums_add_count = ["aesthetic/cryotherapy_room/2", "depart/room/count"]
        if input_depart_room_nums_add_count is not None:
            for add_count_input in input_depart_room_nums_add_count:
                split_list = add_count_input.split("/")
                depart_name = split_list[0]
                room_name = split_list[1]
                add_count = int(split_list[2])
                if department.get_name() == depart_name:
                    for room in department.get_room_config_list().get_room_list():
                        if room.get_name() == room_name:
                            room_raw_count = int(room.get_count())
                            room_new_count = room_raw_count + add_count
                            room_add_area = add_count * float(room.get_area())
                            if outpatient_area_residual - room_add_area > 0:
                                room.set_count(int(room_new_count))
                                outpatient_area_residual -= room_add_area
                                print(f'{depart_name}的{room_name}数量增加{add_count}成功，增加后数量为{room.get_count()}')
                            else:
                                '''所填写超出剩余部分面积，则不添加，抛出一个错误'''
                                print(f'{depart_name}的{room_name}数量增加{add_count}失败：超出剩余部分面积')
                                continue

        # 增加部门交通走廊的宽度
        if input_depart_corridor_width is not None:
            for new_depart_corridor_width in input_depart_corridor_width:
                split_list = new_depart_corridor_width.split("/")
                depart_name = split_list[0]
                new_corridor_width = split_list[1]
                if department.get_name() == depart_name:
                    raw_corridor_width = department.get_corridor_width()
                    print(raw_corridor_width)
                    if float(new_corridor_width) > float(raw_corridor_width):
                        raw_traffic_area = department.get_total_necessary_traffic_area()  # 原有交通总面积
                        add_traffic_area = raw_traffic_area * \
                                           (float(new_corridor_width) / float(raw_corridor_width))  # 乘比例系数后的新交通面积
                        if outpatient_area_residual - add_traffic_area > 0:
                            new_traffic_area = raw_traffic_area + add_traffic_area
                            department.set_total_necessary_traffic_area(new_traffic_area)
                            outpatient_area_residual -= add_traffic_area
                            print(
                                f'{depart_name}的走廊宽度已设置为{new_corridor_width}，总交通面积增加了{add_traffic_area}，增加后为{new_traffic_area}')

                        else:
                            '''所填写超出剩余部分面积，则不添加，抛出一个错误'''
                            print(f'{depart_name}的走廊宽度增加失败：超出剩余部分面积')


def write_department_area_from_necessary_total_area(depart_list):
    """
    将计算完成后的必要面积写入科室总面积之中，如果没有策略一、策略二的面积增项，该值相同
    :param depart_list: 门诊持有的科室列表
    :return:
    """
    for department in depart_list.get_department_list():
        department.set_department_area(department.get_necessary_total_area())

def cal_department_floor_num(depart_list, raw_floor_num, opd_land_area):
    """
    计算门诊中各个科室的楼层数，根据floor_weight进行排布：
    1、floor_weight越大的排布优先在底层
    2、不允许科室跨层排布，科室房间的层数继承科室楼层数

    :param depart_list: 门诊持有的科室列表
    :param raw_floor_num: 原有计算出的门诊楼层数
    :param opd_land_area: 门诊楼占地面积--门诊单层能够排布的最大面积
    :return:
    """

    department_list = depart_list.get_department_list()
    sorted_floor_weight_depart_list = sorted(department_list,
                                             key=lambda obj: obj.floor_weight, reverse=True)        # 按照floor_weight排序
    raw_floor_num = int(raw_floor_num)                                                              # 原始计算出楼层数
    floor_area = float(opd_land_area)                                                               # 门诊占地面积

    for floor in range(len(sorted_floor_weight_depart_list)):                                       # 最大层数不大于科室数目
        area = floor_area
        for depart in sorted_floor_weight_depart_list:
            depart_area = depart.get_department_area()                                              # 拿到本科室的科室面积
            if depart.get_design_floor() is None:                                                   # 找到还没有设置楼层的科室
                if area >= depart_area:                                                             # 本层剩余面积比科室需要的面积大
                    area -= depart_area
                    depart.set_design_floor(floor + 1)                                              # 将本科室设置在该层
                    print(f'{depart.get_name()}安排在{depart.get_design_floor()}层')
                else:
                    # 如果本层的剩余面积比科室的需求面积小-跳出当前循环，进入下一个楼层之中
                    break

    # 检查看一下是否有没有排布下的科室
    for depart in sorted_floor_weight_depart_list:
        if depart.get_design_floor() is None:
            raise ValueError(f'{depart.get_name()}没有排布')

    # 判断差距有几层
    max_depart_floor = 0
    for depart in sorted_floor_weight_depart_list:
        depart_floor = depart.get_design_floor()
        if max_depart_floor < depart_floor:
            max_depart_floor = depart_floor
        else:
            continue
    print(f'原有计算出的门诊楼层数{raw_floor_num},排布科室后最大层数为{max_depart_floor}，'
          f'差距为{max_depart_floor - raw_floor_num}层')

    # 差距过大抛出一个错误
    floor_differ_allow_max = 2
    if max_depart_floor - raw_floor_num > floor_differ_allow_max:
        raise ValueError(f'检查楼层排布，楼层计算差值超出设定允许范围，差值为{max_depart_floor - raw_floor_num}层')

    # 将科室层数写入房间之中
    for depart in sorted_floor_weight_depart_list:
        depart_room_list = depart.get_room_config_list()
        depart_floor = depart.get_design_floor()
        for room in depart_room_list.get_room_list():
            room.set_floor(depart_floor)


