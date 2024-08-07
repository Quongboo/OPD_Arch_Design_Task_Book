import csv
import inspect

'''基础的实体类之中包括to_json,from_json两个方法'''


class BaseEntity:

    def __init__(self):
        pass

    def to_json(self):
        deserialize_value = {}

        curr_func_name = inspect.currentframe().f_code.co_name  # 获取当前函数变量名
        paraments = inspect.signature(self.__init__).parameters  # 获取当前函数的参数列表
        for key, _ in paraments.items():
            value = getattr(self, key)  # 获取值
            # List[Room] RoomEntityList--做to_json和for_json
            if hasattr(value, curr_func_name):  # 检查函数值是否有to_json方法
                deserialize_value[key] = getattr(value, curr_func_name)()  # 有的话将值返回到key中
            else:
                deserialize_value[key] = getattr(self, key)  # 没有的话将属性值直接赋给他
        return deserialize_value

    @classmethod
    def from_json(cls, value_dict: dict):
        curr_func_name = inspect.currentframe().f_code.co_name  # 获取当前函数的名称--from_json
        init_paramenters = inspect.signature(cls.__init__).parameters  # 获取__init__初始化值的列表
        value_ = {}
        # print(value_dict)
        for key, value in value_dict.items():
            # print(key, value)
            if key not in init_paramenters.keys():  # 如果不在__init__初始化值列表中的就过滤
                print('输入值不在类的__init__之中')
                continue
            else:
                class_ = init_paramenters[key].annotation  # 获取数据类型int\float...
                if hasattr(class_, curr_func_name):  # 检查当前对象中是否有from_json方法
                    # print(getattr(class_, curr_func_name))
                    value_[key] = getattr(class_, curr_func_name)(value)  # 调用class_对象的from_json方法//是否是双重字典
                else:
                    value_[key] = value
        # print("value_ ", value_)
        return cls(**value_)  # 使用键值作为参数返回一个实例

