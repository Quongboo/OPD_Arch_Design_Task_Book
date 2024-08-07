from typing import List
from math import ceil
from entity.base_entity import BaseEntity
from handler.department.deparment_brief_handler \
    import (
        cal_weight_for_department_patient,
        cal_department_patient_nums,
        cal_medical_mix_surgery_department_patient_nums,
        cal_department_examination_nums,
        cal_department_examination_total_nums,
        depart_cal_room_name_list,
        cal_department_none_examination,
        cal_department_room_count,
        cal_department_necessary_room,
        cal_department_necessary_area_from_room,
        cal_department_necessary_traffic_area,
        cal_department_necessary_total_area)
from handler.utils.io_handler import read_json
from entity.room import RoomEntity, RoomEntityList
import inspect


class DepartBase:
    """科室人数计算--逻辑基础类"""
    __support_name__ = []
    __support_class_weight__ = {}
    __support_class_value__ = {}  # 计算得到的值

    def query_class_value(self, class_name: str):
        return self.__support_class_value__[class_name]


class DepartStandard(DepartBase):
    """国家规范标准相关的计算-->规范区分人数"""

    __support_name__ = ["surgery_class", "medical_class", "gynecology_class",
                        "obstetrics_class", "pediatrics_class",
                        "otolaryngology_eye_class", "tcm_class", "other_class",
                        ]
    __support_class_weight__ = {"surgery_class": 0.28,
                                "medical_class": 0.25,
                                "gynecology_class": 0.15,
                                "obstetrics_class": 0.03,
                                "pediatrics_class": 0.08,
                                "otolaryngology_eye_class": 0.10,
                                "tcm_class": 0.05,
                                "other_class": 0.06}

    def cal_standard_value(self, total_patient_nums: int):
        self.__support_class_value__ = {
            key: ceil(weight * total_patient_nums)
            for key, weight in self.__support_class_weight__.items()
        }
        print('国家标准计算的类型人数', self.__support_class_value__)


class DepartmentEntity(BaseEntity):
    """
    医院科室实体类
    """

    def __init__(self,
                 name: str,
                 region_class: str,
                 standard_class: str,
                 type_class: str,

                 patient_weight: float,
                 mix_inter_med_weight: float,
                 mix_outer_med_weight: float,
                 floor_weight: float,
                 traffic_weight: float,
                 layout_weight: float,

                 patient_nums: int,
                 per_doctor_hour_reception: float,
                 doctor_nums_per_examination: int,
                 department_area: float,
                 room_config_list: RoomEntityList = None

                 ):
        """

        :param name:                            科室名称
        :param region_class:                    科室诊区名称
        :param standard_class:                  科室国家规范类名称
        :param type_class:                      科室人数计算类名
        :param patient_weight:                  科室人数权重
        :param mix_inter_med_weight:            内科占比权重
        :param mix_outer_med_weight:            外科占比权重
        :param floor_weight:                    楼层权重
        :param traffic_weight:                  交通权重
        :param layout_weight:                   布局权重
        :param patient_nums:                    科室患者数量
        :param per_doctor_hour_reception:       科室医生效率
        :param doctor_nums_per_examination:     每间诊室医生人数
        :param department_area:                 科室总面积
        """

        super().__init__()
        self.name = name
        self.region_class = region_class
        self.standard_class = standard_class
        self.type_class = type_class

        self.patient_weight = patient_weight
        self.mix_inter_med_weight = mix_inter_med_weight
        self.mix_outer_med_weight = mix_outer_med_weight
        self.floor_weight = floor_weight
        self.traffic_weight = traffic_weight
        self.layout_weight = layout_weight

        self.patient_nums = patient_nums
        self.per_doctor_hour_reception = per_doctor_hour_reception
        self.doctor_nums_per_examination = doctor_nums_per_examination
        self.department_area = department_area                              # 科室总设计面积，提供楼层排布使用

        self.consulting_room_nums = 0                                       # 科室诊室数量
        self.room_config_list = room_config_list                            # 科室支持的房间配置文件
        self.necessary_room_list = None                                     # 必要房间的需求表
        self.depart_necessary_area_from_room = None                         # 必要部分房间内部面积
        self.total_necessary_traffic_area = None                            # 必要房间部分计算得出的科室内部交通面积
        self.necessary_total_area = None                                    # 科室必要的总面积 == 科室最小面积
        self.corridor_width = 2.4                                           # 科室走廊宽度
        self.design_floor = None                                            # 科室楼层

    def get_design_floor(self):
        return self.design_floor

    def set_design_floor(self, design_floor: int):
        self.design_floor = design_floor

    def get_department_area(self):
        return self.department_area

    def set_department_area(self, department_area: float):
        self.department_area = department_area

    def get_corridor_width(self):
        return self.corridor_width

    def set_corridor_width(self, corridor_width: float):
        self.corridor_width = corridor_width

    def get_necessary_total_area(self):
        return self.necessary_total_area

    def set_necessary_total_area(self, necessary_total_area: float):
        self.necessary_total_area = necessary_total_area

    def get_total_necessary_traffic_area(self):
        return self.total_necessary_traffic_area

    def set_total_necessary_traffic_area(self, total_necessary_traffic_area: float):
        self.total_necessary_traffic_area = total_necessary_traffic_area

    def get_depart_necessary_area_from_room(self):
        return self.depart_necessary_area_from_room

    def set_depart_necessary_area_from_room(self, depart_necessary_area_from_room: float):
        self.depart_necessary_area_from_room = depart_necessary_area_from_room

    def get_necessary_room_list(self) -> List[RoomEntity]:
        return self.necessary_room_list

    def set_necessary_room_list(self, necessary_room_list: List):
        self.necessary_room_list = necessary_room_list

    def get_room_config_list(self) -> RoomEntityList:
        return self.room_config_list

    def set_room_config_list(self, room_file: str):
        """
        配置科室的房间
        :param room_file: 房间配置文件json
        :return:
        """

        data = read_json(room_file)
        room_config_list = []
        for depart, room_list in data.items():
            if depart == self.get_name():
                for room in room_list:
                    params = inspect.signature(RoomEntity).parameters  # 获取RoomEntity的参数
                    kwargs = {key: room.get(key, None) for key in params.keys()}  # 从房间字典中获取对应参数的值
                    room_class = RoomEntity(**kwargs)  # 使用关键字参数创建RoomEntity对象
                    room_config_list.append(room_class)
        room_config_proxy = RoomEntityList(room_config_list)

        self.room_config_list = room_config_proxy

    def get_name(self):
        return self.name

    def get_region_class(self):
        return self.region_class

    def get_standard_class_name(self):
        return self.standard_class

    def get_type_class_name(self):
        return self.type_class

    def get_patient_weight(self):
        return self.patient_weight

    def set_patient_weight(self, patient_weight: float):
        self.patient_weight = patient_weight

    def get_layout_weight(self):
        return self.layout_weight

    def get_mix_inter_med_weight(self):
        return self.mix_inter_med_weight

    def get_mix_outer_med_weight(self):
        return self.mix_outer_med_weight

    def get_floor_weight(self):
        return self.floor_weight

    def get_traffic_weight(self):
        return self.traffic_weight

    def get_patient_nums(self):
        return self.patient_nums

    def set_patient_nums(self, patient_nums: int):
        self.patient_nums = patient_nums

    def get_per_doctor_hour_reception(self):
        return self.per_doctor_hour_reception

    def get_doctor_nums_per_examination(self):
        return self.doctor_nums_per_examination

    def get_consulting_room_nums(self):
        return self.consulting_room_nums

    def set_consulting_room_nums(self, consulting_room_nums):
        self.consulting_room_nums = consulting_room_nums


class DepartmentEntityList:
    """
    科室实体列表类
    """

    def __init__(self, department_list: List[DepartmentEntity]):
        self.department_list = department_list
        self.standard_proxy = DepartStandard()
        # self.type_proxy = DepartType()
        # self.mix_type_proxy = DepartMixType()

    def get_department_list(self):
        return self.department_list

    def set_department_list(self, department_list: List[DepartmentEntity]):
        self.department_list = department_list

    def filter_valid_department(self, required_depart_list: List[str]):
        self.department_list = [department for department in self.department_list
                                if department.get_name() in required_depart_list]
        print(f"过滤后的有效科室有{len(self.department_list)}个:{self.department_list}")

    def to_json(self):
        return [depart_entity.to_json() for depart_entity in self.department_list]

    @classmethod
    def from_json(cls, depart_value_list: list):
        print("check depart_value_list is None------", depart_value_list is None)
        # print(depart_value_list)
        return cls(
            [DepartmentEntity.from_json(depart_content)
             for depart_content in depart_value_list]
        )

    def design_department_brief(self, total_patient_num: int):
        """
        科室任务书计算过程：
        1、科室患者人数计算
        2、科室诊室数计算及房间配置
        3、科室面积计算
        :param total_patient_num: 医院门诊患者人数建议值
        :return:
        """

        self.standard_proxy.cal_standard_value(total_patient_num)                   # 按照国家标准计算人数分类方式
        cal_weight_for_department_patient(self.department_list)                     # 更新计算各个科室类型用于计算患者人数的权重
        cal_department_patient_nums(self.department_list, self.standard_proxy)      # 计算普通科室患者人数分配
        cal_medical_mix_surgery_department_patient_nums(self.department_list)       # 计算内外科混合科室患者人数分配

        cal_department_examination_nums(self.department_list)                       # 计算科室中诊室数量
        cal_department_examination_total_nums(self.department_list)                 # 打印医院门诊诊室总数
        depart_cal_room_name_list(self.department_list)                             # 打印参与房间数量计算的科室数量及名称
        cal_department_none_examination(self.department_list)                       # 检查科室中是否有诊室--打印没有诊室的科室
        cal_department_room_count(self.department_list)                             # 配置科室房间数并写入诊室数量
        cal_department_necessary_room(self.department_list)                         # 计算科室必要房间

        cal_department_necessary_area_from_room(self.department_list)               # 计算科室房间的面积
        cal_department_necessary_traffic_area(self.department_list)                 # 计算必要部分交通面积
        cal_department_necessary_total_area(self.department_list)                   # 计算科室必要面积

    def department_room_name_area_dict(self, depart):
        """
        获取科室含有房间名称及面积的字典
        :return: 房间名称及面积字典
        """
        room_area_dict = {}
        room_list = depart.get_necessary_room_list()
        for room in room_list:
            _name = room.get_name()
            _area = room.get_area()
            room_area_dict[_name] = _area
        # print(room_area_dict)
        return room_area_dict

    def write_csv_department(self, department_csv_path: str):
        """
        将所有科室写为一个csv文件
        :return:
        """
        # 科室必要房间名称及表面积
        import csv
        fieldnames = ["科室名称", '科室诊区名称', '科室国家规范类名称', '科室人数计算类名', '科室人数权重', '内科占比权重', '外科占比权重',
                      '楼层权重', '交通权重', '布局权重', '科室患者数量', '科室医生效率', '每间诊室医生人数', '科室总面积', '科室诊室数量',
                      '科室必要房间配置表（名称+面积）', '科室必要房间面积', '科室必要交通面积',  '科室必要总面积', '科室走廊宽度',
                      '科室楼层数'
                      ]

        with open(department_csv_path, 'w', newline='', encoding='utf-8')as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            department = self.get_department_list()

            for depart in department:
                room_name_area_dict = self.department_room_name_area_dict(depart)

                writer.writerow({
                    '科室名称': depart.get_name(),
                    '科室诊区名称': depart.get_region_class(),
                    '科室国家规范类名称': depart.get_standard_class_name(),
                    '科室人数计算类名': depart.get_type_class_name(),
                    '科室人数权重': depart.get_patient_weight(),
                    '内科占比权重': depart.get_mix_inter_med_weight(),
                    '外科占比权重': depart.get_mix_outer_med_weight(),
                    '楼层权重': depart.get_floor_weight(),
                    '交通权重': depart.get_traffic_weight(),
                    '布局权重': depart.get_layout_weight(),
                    '科室患者数量': depart.get_patient_nums(),
                    '科室医生效率': depart.get_per_doctor_hour_reception(),
                    '每间诊室医生人数': depart.get_doctor_nums_per_examination(),
                    '科室总面积': depart.get_department_area(),
                    '科室诊室数量': depart.get_consulting_room_nums(),
                    '科室必要房间配置表（名称+面积）': room_name_area_dict,
                    '科室必要房间面积': depart.get_depart_necessary_area_from_room(),
                    '科室必要交通面积': depart.get_total_necessary_traffic_area(),
                    '科室必要总面积': depart.get_necessary_total_area(),
                    '科室走廊宽度': depart.get_corridor_width(),
                    '科室楼层数': depart.get_design_floor()
                })
        print(f'科室信息--csv保存成功：{department_csv_path}')

    def write_csv_depart_room(self, depart_room_csv_path: str):
        import csv
        """
        储存详细的科室房间配置文件为一个整体的csv文件
        TODO：考虑储存为每个科室门诊一个单独的csv文件
        1、获取科室-房间信息
        2、将房间信息写入csv，第一列是所属的科室
        :param depart_room_csv_path: 科室房间csv储存地址
        :return: 
        """
        # 房间储存信息

        fieldnames = ['所属科室', '房间名称', '房间描述', '房间数量', '房间面积', '房间面宽', '房间进深', '房间高度',
                      '房间类型', '房间楼层', '房间医生数量', '交通通达性权重', '平面布局权重', '窗子权重', '最小面积', '最大面积',
                      '最小数量', '最大数量']
        with open(depart_room_csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            department = self.get_department_list()
            for depart in department:
                room_list = depart.get_necessary_room_list()
                for room in room_list:
                    writer.writerow({
                        '所属科室': depart.get_name(),
                        '房间名称': room.get_name(),
                        '房间描述': room.get_desc(),
                        '房间数量': room.get_count(),
                        '房间面积': room.get_area(),
                        '房间面宽': room.get_width(),
                        '房间进深': room.get_length(),
                        '房间高度': room.get_height(),
                        '房间类型': room.get_room_type(),
                        '房间楼层': room.get_floor(),
                        '房间医生数量': room.get_doctor_num(),
                        '交通通达性权重': room.get_access_weight(),
                        '平面布局权重': room.get_layout_weight(),
                        '窗子权重': room.get_windows_weight(),
                        '最小面积': room.get_min_area(),
                        '最大面积': room.get_max_area(),
                        '最小数量': room.get_min_count(),
                        '最大数量': room.get_max_count()
                    })
        print(f'科室-房间--csv文件按保存成功：{depart_room_csv_path}')





