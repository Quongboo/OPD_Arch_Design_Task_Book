from front import brief_demo

"""
目前支持任务书数据生成
"""

if __name__ == "__main__":

    args = brief_demo.get_args()
    print(args)
    brief_demo.webui(args)