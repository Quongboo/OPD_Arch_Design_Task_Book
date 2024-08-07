from typing import List

from entity.base_entity import BaseEntity


class RoomEntity(BaseEntity):
    """
    科室房间实体类
    """

    def __init__(self,
                 name: str,
                 desc: str,

                 count: int,
                 area: float,
                 width: float,
                 length: float,
                 height: float,

                 room_type: str,
                 floor: int,
                 doctor_num: int,

                 access_weight: float,
                 layout_weight: float,
                 windows_weight: float,

                 min_area: float,
                 max_area: float,

                 min_count: int,
                 max_count: int,
                 ):
        """

        :param name:                房间名称
        :param desc:                房间描述
        :param count:               房间数量
        :param area:                房间面积
        :param width:               房间面宽
        :param length:              房间进深
        :param height:              房间高度
        :param room_type:           房间类型
        :param floor:               房间楼层
        :param doctor_num:          房间医生数量
        :param access_weight:       交通通达性权重
        :param layout_weight:       平面布局权重
        :param windows_weight:      窗子权重
        :param min_area:            最小面积
        :param max_area:            最大面积
        :param min_count:           最小数量（必要的房间最小数量为1）
        :param max_count:           最大数量
        """
        super().__init__()

        self.name = name
        self.desc = desc

        self.count = count
        self.area = area
        self.width = width
        self.length = length
        self.height = height

        self.room_type = room_type
        self.floor = floor
        self.doctor_num = doctor_num

        self.access_weight = access_weight
        self.layout_weight = layout_weight
        self.windows_weight = windows_weight

        self.min_area = min_area
        self.max_area = max_area

        self.min_count = min_count
        self.max_count = max_count

    def get_name(self):
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_desc(self):
        return self.desc

    def set_desc(self, desc: str):
        self.desc = desc

    def get_count(self):
        return self.count

    def set_count(self, count: int):
        self.count = count

    def get_area(self):
        return self.area

    def set_area(self, area: float):
        self.area = area

    def get_width(self):
        return self.width

    def set_width(self, width: float):
        self.width = width

    def get_length(self):
        return self.length

    def set_length(self, length: float):
        self.length = length

    def get_height(self):
        return self.height

    def set_height(self, height: float):
        self.height = height

    def get_room_type(self):
        return self.room_type

    def set_room_type(self, room_type: str):
        self.room_type = room_type

    def get_floor(self):
        return self.floor

    def set_floor(self, floor: int):
        self.floor = floor

    def get_doctor_num(self):
        return self.doctor_num

    def set_doctor_num(self, doctor_num: int):
        self.doctor_num = doctor_num

    def get_access_weight(self):
        return self.access_weight

    def set_access_weight(self, access_weight: float):
        self.access_weight = access_weight

    def get_layout_weight(self):
        return self.layout_weight

    def set_layout_weight(self, layout_weight: float):
        self.layout_weight = layout_weight

    def get_windows_weight(self):
        return self.windows_weight

    def get_min_area(self):
        return self.min_area

    def set_min_area(self, min_area: float):
        self.min_area = min_area

    def get_max_area(self):
        return self.max_area

    def set_max_area(self, max_area: float):
        self.max_area = max_area

    def get_min_count(self):
        return self.min_count

    def set_min_count(self, min_count: int):
        self.min_count = min_count

    def get_max_count(self):
        return self.max_count

    def set_max_count(self, max_count: int):
        self.max_count = max_count


class RoomEntityList:
    """
    房间实体列表
    """

    def __init__(self,
                 room_list: List[RoomEntity]):
        self.room_list = room_list

    def get_room_list(self) -> List[RoomEntity]:
        return self.room_list

    def set_room_list(self, room_list: List[RoomEntity]):
        self.room_list = room_list

    def to_json(self):
        return [room.to_json() for room in self.room_list]
