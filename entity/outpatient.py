import inspect
import math
from typing import List
from entity.department import DepartmentEntityList
from entity.base_entity import BaseEntity
from handler.outpatient.outpatient_brief_handler \
    import (
        cal_outpatient_land_area,
        cal_outpatient_floor_num,
        cal_outpatient_max_build_area,
        cal_outpatient_min_build_area,
        cal_outpatient_daily_patient_nums,
        cal_outpaint_total_patient_nums,
        cal_outpatient_area_necessary,
        cal_excess_outpatient_area,
        cal_add_outpatient_public_traffic_area,
        cal_excess_area_for_department,
        cal_add_count_for_depart_room,
        cal_input_add_area_or_count_for_depart_room,
        write_department_area_from_necessary_total_area,
        cal_department_floor_num)


class OutpatientEntity(BaseEntity):

    def __init__(self,
                 land_area: float = None,
                 floor_num: int = None,
                 min_build_area: float = None,
                 max_build_area: float = None,
                 suggest_patient_num: int = None,
                 input_design_build_area: float = None,
                 department_list: DepartmentEntityList = None
                 ):
        """

        :param land_area: 门诊占地面积
        :param floor_num: 门诊楼层数
        :param min_build_area: 门诊建筑面积最小值
        :param max_build_area: 门诊建筑面积最大值
        :param suggest_patient_num:门诊患者人数建议值
        :param input_design_build_area:设计建筑面积(输入值)
        :param department_list:门诊科室列表
        """

        super().__init__()
        self.land_area = land_area
        self.floor_num = floor_num
        self.min_build_area = min_build_area
        self.max_build_area = max_build_area
        self.suggest_patient_num = suggest_patient_num
        self.department_list = department_list
        self.input_design_build_area = input_design_build_area

        self.patient_nums = 0  # 由各科确定的患者人数
        self.outpatient_area_necessary = None
        self.outpatient_traffic_area = 0.

    def get_patient_nums(self):
        return self.patient_nums

    def set_patient_nums(self, patient_nums: int):
        self.patient_nums = patient_nums

    def get_outpatient_traffic_area(self):
        return self.outpatient_traffic_area

    def set_outpatient_traffic_area(self, outpatient_traffic_area: float):
        self.outpatient_traffic_area = outpatient_traffic_area

    def get_land_area(self):
        return self.land_area

    def get_floor_num(self):
        return self.floor_num

    def get_suggest_patient_num(self):
        return self.suggest_patient_num

    def get_outpatient_area_necessary(self):
        return self.outpatient_area_necessary

    def set_outpatient_area_necessary(self, outpatient_area_necessary: float):
        self.outpatient_area_necessary = outpatient_area_necessary

    def get_department_entity_list(self):
        return self.department_list

    def get_input_design_build_area(self):
        return self.input_design_build_area

    def get_min_build_area(self):
        return self.min_build_area

    def get_max_build_area(self):
        return self.max_build_area

    def cal_land_area(self):
        if self.land_area is not None:
            return self.land_area
        else:
            return cal_outpatient_land_area()

    def design_brief(self,
                     hospital_area: float,
                     service_people_nums: int,
                     need_bed_nums: int,
                     residual_area_method2_config: dict,
                     residual_area_method: str
                     ):
        """
        门诊楼相关计算过程
        :param residual_area_method:    剩余面积的分配模式（模式一、模式二）
        :param hospital_area:           医院面积
        :param service_people_nums:     医院服务人数
        :param need_bed_nums:           医院床位数
        :param residual_area_method2_config:  面积增加策略二的配置项
        :return:
        """

        self.land_area = self.cal_land_area()  # 门诊占地面积
        self.min_build_area = cal_outpatient_min_build_area(hospital_area)  # 门诊建筑面积最小值
        self.max_build_area = cal_outpatient_max_build_area(hospital_area)  # 门诊建筑面积最大值
        self.floor_num = cal_outpatient_floor_num(self.land_area, self.max_build_area)  # 门诊楼层数
        self.suggest_patient_num = \
            cal_outpatient_daily_patient_nums(service_people_nums, need_bed_nums)  # 门诊患者人数建议值

        """科室计算入口"""
        self.department_list.design_department_brief(self.suggest_patient_num)  # 门诊科室相关信息

        self.set_patient_nums(
            cal_outpaint_total_patient_nums(self.get_department_entity_list().get_department_list()))  # 科室汇总的门诊患者数

        opd_necessary_area = cal_outpatient_area_necessary(
            self.get_department_entity_list().get_department_list())

        self.set_outpatient_area_necessary(opd_necessary_area)  # 门诊必要值面积（最小面积）

        excess_outpatient_area = cal_excess_outpatient_area(self.get_outpatient_area_necessary(),
                                                            self.get_input_design_build_area(),
                                                            self.get_min_build_area(),
                                                            self.get_max_build_area())  # 门诊楼可增加面积（差值）

        add_outpatient_traffic_area = cal_add_outpatient_public_traffic_area(excess_outpatient_area)  # 门诊增加交通面积
        self.set_outpatient_traffic_area(add_outpatient_traffic_area + self.get_outpatient_traffic_area())

        outpatient_area_residual = cal_excess_area_for_department(
            excess_outpatient_area, add_outpatient_traffic_area)  # 门诊科室可分配的面积

        # 设计：用户输入决定是使用分配策略一、分配策略二
        """
        剩余部分面积增加设计：用户输入决定是使用分配策略一、分配策略二
        门诊剩余面分配策略一：增加layout_weight大的房间数量
        门诊剩余面分配策略二：根据输入，依次添加能够添加的房间和数量
        """
        if residual_area_method == "method1":
            print("门诊剩余面分配策略一")
            cal_add_count_for_depart_room(outpatient_area_residual, self.department_list)
        elif residual_area_method == "method2":
            print("门诊剩余面分配策略二")
            cal_input_add_area_or_count_for_depart_room(outpatient_area_residual, self.department_list,
                                                        residual_area_method2_config)
        else:
            pass

        write_department_area_from_necessary_total_area(self.department_list)  # 将确定的科室面积写入科室面积字段

        cal_department_floor_num(self.department_list, self.get_floor_num(), self.get_land_area())  # 计算每一个科室的层数

    def outpatient_depart_name_area_dict(self):
        """
        获取门诊含有的科室名称及面积
        :return:门诊名称及面积字典
        """
        depart_name_area_dict = {}
        for depart in self.department_list.get_department_list():
            d_name = depart.get_name()
            d_area = depart.get_necessary_total_area()
            depart_name_area_dict[d_name] = d_area
        # print(depart_name_area_dict)
        return depart_name_area_dict

    def write_csv_outpatient(self, outpatient_csv_path: str):
        """
        储存门诊部为一个csv文件
        :param outpatient_csv_path:门诊csv的储存路径
        :return:
        """
        import csv
        with open(outpatient_csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # 门诊基础信息
            data = [
                ['名称', '值'],
                ['门诊占地面积', f'{self.get_land_area()}'],
                ['门诊楼层数', f'{self.get_floor_num()}'],
                ['门诊建筑面积最小值(建议)', f'{self.get_min_build_area()}'],
                ['门诊建筑面积最大值(建议)', self.get_max_build_area()],
                ['门诊患者人数建议值', f'{self.get_suggest_patient_num()}'],
                ['设计建筑面积(输入值)', f'{self.get_input_design_build_area()}'],

                ['门诊计算得出患者人数', f'{self.get_patient_nums()}'],
                ['门诊必要建筑面积（最小建筑面积）', f'{self.get_outpatient_area_necessary()}'],
                ['门诊增加的交通面积', f'{self.get_outpatient_traffic_area()}'],
            ]
            writer.writerows(data)
            # 门诊科室信息
            depart_name_area_dict = self.outpatient_depart_name_area_dict()
            depart_name_area_list = [depart_name_area_dict]
            writer.writerow(["门诊科室及面积信息如下"])
            writer.writerow(depart_name_area_list)

        print(f'门诊部信息--csv保存成功：{outpatient_csv_path}')


class OutpatientEntityList:

    def __init__(self,
                 outpatient_list: List[OutpatientEntity]):
        """
        dsc：获取outpatient输入的类
        :param outpatient_list: 持有的门诊对象列表

        """
        super().__init__()
        self.outpatient_list = outpatient_list

    def get_outpatient_list(self):
        return self.outpatient_list

    def set_outpatient_list(self, outpatient_list: List[OutpatientEntity]):
        self.outpatient_list = outpatient_list

    def to_json(self):
        return [outpatient.to_json() for outpatient in self.outpatient_list]

    def filter_valid_department(self, required_depart_list: List[str]):
        [outpatient.department_list.filter_valid_department(required_depart_list)
         for outpatient in self.outpatient_list]

    def design_brief(self,
                     hospital_area: float,
                     service_people_nums: int,
                     need_bed_nums: int,
                     residual_area_method2_config: dict,
                     residual_area_method: str
                     ):
        """

        :param residual_area_method: 剩余面积划分模式
        :param residual_area_method2_config: 剩余面积分配策略二配置文件
        :param hospital_area:           医院建筑面积
        :param service_people_nums:     医院服务人口数
        :param need_bed_nums:           医院床位数
        :return:
        """

        """调用design_brief方法，将输入注入"""

        [outpatient.design_brief(hospital_area, service_people_nums, need_bed_nums,
                                 residual_area_method2_config, residual_area_method)
         for outpatient in self.outpatient_list]

    @classmethod
    def from_json(cls, outpatient_value_list: list):
        """

        :param outpatient_value_list:输入的门诊outpatient_element——json配置文件
        :return:实例化的门诊对象
        """
        # print(len(outpatient_value_list))
        return cls(
            [OutpatientEntity.from_json(outpatient)
             for outpatient in outpatient_value_list]
        )
