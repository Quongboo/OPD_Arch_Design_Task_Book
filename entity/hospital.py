import csv
import inspect
from typing import List
from handler.utils.io_handler import read_json
from entity.department import DepartmentEntity, DepartmentEntityList
from entity.outpatient import OutpatientEntity, OutpatientEntityList
from entity.base_entity import BaseEntity
from handler.hospital.hospital_brief_handler import \
    (cal_hospital_daily_patient_nums,
     cal_hospital_total_building_area,
     cal_hospital_total_land_area,
     cal_people_bed_avg
     )



class HospitalEntity(BaseEntity):
    """
        医院实体类
    """

    def __init__(self,
                 name: str,
                 need_bed_nums: int,
                 need_service_people_nums: int,
                 serialize_outpatient_file: str,
                 serialize_room_file: str,
                 residual_area_method: str,
                 residual_area_method2_config: dict,  # 策略二配置文件
                 required_depart_list: List[str],
                 need_patient_nums: int = None,
                 outpatient_config: OutpatientEntityList = None,

                 ):
        """
        :param name:                        医院名称
        :param need_bed_nums:               需要床位数
        :param need_service_people_nums:    需要服务辖区人口
        :param need_patient_nums:           最大服务病人数量
        :param serialize_outpatient_file:   配置化outpatient-Json文件
        :param required_depart_list:        必须设置科室列表
        """
        super().__init__()
        self.name = name
        self.need_bed_nums = need_bed_nums
        self.need_service_people_nums = need_service_people_nums
        self.need_patient_nums = need_patient_nums
        self.serialize_room_file = serialize_room_file
        self.residual_area_method = residual_area_method
        self.residual_area_method2_config = residual_area_method2_config
        self.serialize_outpatient_file = serialize_outpatient_file
        self.required_depart_list = required_depart_list
        self.outpatient_config = outpatient_config
        self.outpatient_config = self.read_outpatient_config(self.serialize_outpatient_file)

        self.hospital_land_area = 0.  # 医院用地面积
        self.hospital_building_area = 0.  # 医院建筑面积
        self.thousand_people_per_bed = 0.  # 医院千人床位数

    def get_residual_area_method(self):
        return self.residual_area_method

    def get_residual_area_method2_config(self):
        return self.residual_area_method2_config

    def get_hospital_land_area(self):
        return self.hospital_land_area

    def set_hospital_land_area(self, hospital_land_area: float):
        self.hospital_land_area = hospital_land_area

    def get_hospital_building_area(self):
        return self.hospital_building_area

    def set_hospital_building_area(self, hospital_building_area: float):
        self.hospital_building_area = hospital_building_area

    def get_thousand_people_per_bed(self):
        return self.thousand_people_per_bed

    def set_thousand_people_per_bed(self, thousand_people_per_bed: float):
        self.thousand_people_per_bed = thousand_people_per_bed

    def set_department_room_list(self):
        out_list = self.outpatient_config.get_outpatient_list()
        for out in out_list:
            for depart in out.department_list.get_department_list():
                depart.set_room_config_list(self.serialize_room_file)

    def get_name(self):
        return self.name

    def get_need_bed_nums(self):
        return self.need_bed_nums

    def get_need_service_people_nums(self):
        return self.need_service_people_nums

    def get_need_patient_nums(self):
        return self.need_patient_nums

    def get_serialize_outpatient_file(self):
        return self.serialize_outpatient_file

    def get_outpatient_config(self):
        return self.outpatient_config

    def get_required_depart_list(self):
        return self.required_depart_list

    def set_required_depart_list(self, required_depart_list: List[str]):
        self.required_depart_list = required_depart_list

    def read_outpatient_config(self, serialize_outpatient_file: str) -> OutpatientEntityList:
        """
        :param serialize_outpatient_file:  配置化outpatient-Json文件
        :return: 实例化的门诊列表
        """
        if self.outpatient_config is not None:
            return self.outpatient_config
        else:
            outpatient_content_list = read_json(serialize_outpatient_file)
            # print("读取门诊配置文件：outpatient_element", outpatient_content_list)
            return OutpatientEntityList.from_json(outpatient_content_list)

    def design_brief(self):
        """
        医院任务书计算入口函数
        """
        # 医院相关计算
        hospital_land_area = cal_hospital_total_land_area(self.need_bed_nums)
        hospital_building_area = cal_hospital_total_building_area(self.need_bed_nums)
        thousand_people_per_bed = cal_people_bed_avg(self.need_bed_nums, self.need_service_people_nums, rate=1000)

        self.set_hospital_land_area(hospital_land_area)
        self.set_hospital_building_area(hospital_building_area)
        self.set_thousand_people_per_bed(thousand_people_per_bed)

        print(f'医院用地面积：{hospital_land_area}，'
              f'医院建筑面积：{hospital_building_area}，'
              f' 千人床位数：{thousand_people_per_bed}')

        # 门诊相关计算
        self.outpatient_config.filter_valid_department(self.required_depart_list)  # 过滤科室
        self.set_department_room_list()  # 配置过滤后的各个科室的房间基础信息表

        self.outpatient_config.design_brief(self.get_hospital_building_area(),
                                            self.get_need_service_people_nums(),
                                            self.get_need_bed_nums(),
                                            self.get_residual_area_method2_config(),
                                            self.get_residual_area_method())  # 门诊部门任务书计算

        # 住院部相关计算
        # TODO：医院其他科室任务计算阶段开发

    def write_csv_hospital(self, hospital_csv_path):
        with open(hospital_csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            data = [
                ['名称', '值'],
                ['医院名称', f'{self.get_name()}'],
                ['需要的床位数', f'{self.get_need_bed_nums()}'],
                ['需要服务辖区人口', f'{self.get_need_service_people_nums()}'],
                ['最大服务病人数量', self.get_need_patient_nums()],
                ['医院占地面积建议值', f'{self.get_hospital_land_area()}'],
                ['医院建筑面积最大值', f'{self.get_hospital_building_area()}'],
                ['医院千人床位数', f'{self.get_thousand_people_per_bed()}'],
                ['门诊配置科室列表', f'{self.get_required_depart_list()}'],
            ]
            writer.writerows(data)
