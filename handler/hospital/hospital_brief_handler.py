from handler.outpatient.outpatient_brief_handler import cal_outpatient_daily_patient_nums
"""
综合医院计算文件：
1、医院门诊日均患者人数
2、医院占地面积
3、医院建筑面积
4、医院千人床位数
"""

# 配置项：综合医院建设标准-->根据床位数确定建筑面积以及用地面积指标项
area_from_bed_list = [[0, 199, 117, 110], [200, 499, 115, 113], [500, 799, 113, 116], [800, 1199, 111, 114],
                      [1200, 1500, 109, 112]]


def cal_hospital_daily_patient_nums(service_people_nums: int,
                                    need_bed_nums: int):
    """

    :param service_people_nums: 医院服务片区人数
    :param need_bed_nums: 医院所需床位数
    :return: 医院门诊每天的患者人数
    """
    return cal_outpatient_daily_patient_nums(service_people_nums, need_bed_nums)


def cal_hospital_area_range(need_bed_nums: int,
                            ):
    """

    :param need_bed_nums: 需要的床位数
    :return: 医院面积指标选择区间
    """
    global area_from_bed_list
    for index in range(len(area_from_bed_list)):
        if area_from_bed_list[index][0] <= need_bed_nums <= area_from_bed_list[index][1]:
            return area_from_bed_list[index]
    raise ValueError(f"need_bed_nums: {need_bed_nums} input error")



def cal_hospital_total_land_area(bed_num):
    """

    :param bed_num: 医院床位数
    :return: 医院占地面积建议值
    """
    _, _, land_multi, area_multi = cal_hospital_area_range(bed_num)
    land_area = bed_num * land_multi
    return land_area



def cal_hospital_total_building_area(bed_num):
    """

    :param bed_num: 医院床位数
    :return: 医院建筑面积建议值
    """
    _, _, land_multi, area_multi = cal_hospital_area_range(bed_num)
    building_area = bed_num * area_multi
    return building_area


def cal_people_bed_avg(bed_num, service_num, rate=1000):
    """

    :param bed_num: 医院床位数
    :param service_num: 医院服务人数
    :param rate: 除以比例配置（千人）
    :return: 医院千人床位数配比
    """
    thousand_peo_bed_avg = (bed_num * rate) / service_num
    return thousand_peo_bed_avg
