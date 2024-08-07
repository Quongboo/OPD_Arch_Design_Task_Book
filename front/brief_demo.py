import os

import gradio as gr
import argparse
from main import generate_outpatient_brief_webui


# import matplotlib
# matplotlib.use('TkAgg')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

APPTITLE = "综合医院门诊设计辅助工具"


def get_args():
    parser = argparse.ArgumentParser(
        description='医院门诊生成任务书')
    parser.add_argument('--host', default='127.0.0.1', help='IP Host')              # 本地命令
    # parser.add_argument('--host', default='0.0.0.0', help='IP Host')                  # 服务器命令
    parser.add_argument('--port', default=7860,
                        help='port')
    args = parser.parse_args()
    return args


def download_file(name):
    """
    任务书生成的文件路径
    :param name: 医院名称
    :return:
    """
    path_list = []
    hospital_csv_path = f"data_cached/{name}/{name}_hospital_brief.csv"
    outpatient_csv_path = f"data_cached/{name}/{name}_outpatient_brief.csv"
    department_csv_path = f"data_cached/{name}/{name}_department_brief.csv"
    room_csv_path = f"data_cached/{name}/{name}_room_brief.csv"
    path_list.append(hospital_csv_path)
    path_list.append(outpatient_csv_path)
    path_list.append(department_csv_path)
    path_list.append(room_csv_path)

    return path_list


def download_department_config_csv():
    """
    下载科室配置文件
    :return:
    """
    path = "configs/user_download_config/department_config.csv"
    return path


def download_room_config_zip():
    """
    下载房间配置文件
    :return:
    """
    zip_path = "configs/user_download_config/room_config.zip"
    return zip_path


# 加载科室配置文件
department_config_list = ["department_v3"]
depart_config_swap = None


def upload_depart_file(input_file, depart_config_name, depart_config_swap):
    """
    1、写入用户上传的科室配置文件
    2、转化为json储存
    3、返回给用户下一步选择

    :param input_file:上传的文件
    :param depart_config_name: 输入的配置文件命名
    :param depart_config_swap:
    :return:
    """
    print("input_file", input_file)
    import shutil
    import os
    from handler.utils.config_handler import depart_csv_to_json

    global department_config_list
    target_path = f"configs/user/{depart_config_name}.csv"
    shutil.copy(input_file, target_path)
    os.mkdir(f"configs/user/{depart_config_name}")                # 创建文件夹
    json_path = f"configs/user/{depart_config_name}/{depart_config_name}.json"
    depart_csv_to_json(target_path, json_path)
    department_config_list.append(depart_config_name)
    return gr.Dropdown(choices=department_config_list)


# 加载房间配置文件
room_config_list = ['room_v3']
room_config_swap = None


def upload_room_file(zippath, room_config_name, room_config_swap):
    """
    1、将上传的压缩包解压到指定路径
    2、转化为room_json配置文件
    :param zippath: 压缩包地址
    :param room_config_name: 房间配置文件命名
    :return:
    """
    import shutil
    from handler.utils.config_handler import unzip_file, room_csv_to_json
    global room_config_list
    print(zippath)
    target_path = f"configs/user/{room_config_name}.zip"
    shutil.copy(zippath, target_path)
    folder_path = f"configs/user/{room_config_name}"
    unzip_file(target_path, folder_path)  # 将文件解压到文件夹
    room_json_path = f"configs/user/{room_config_name}"
    room_json_name = f"room_{room_config_name}"
    room_csv_to_json(folder_path, room_json_path, room_json_name)  # 将文件写为一个json
    room_config_list.append(room_config_name)
    return gr.Dropdown(choices=room_config_list)


def webui(args):
    # 页面设置
    while True:
        with gr.Blocks(title=f'{APPTITLE}', mode=f'{APPTITLE}') as barkgui:
            gr.Markdown("# <center>- 医院门诊设计任务书生成助手  - </center>")

            # 第一页 医院门诊任务书生成页面
            with gr.Tab("⭐ 医院门诊设计任务书生成"):
                # 输入医院基本信息
                gr.Markdown("## 🐶 输入医院基本信息")
                with gr.Row():
                    with gr.Column():
                        placeholder_name = "医院名称输入在这里"
                        name = gr.Textbox(label="医院名称", lines=1, placeholder=placeholder_name)

                    with gr.Column():
                        placeholder_bed_nums = "医院床位数输入在这里"
                        need_bed_nums = gr.Textbox(label="医院床位数（可输入值：0-1500）", lines=1,
                                                   placeholder=placeholder_bed_nums)

                    with gr.Column():
                        placeholder_serve_nums = "医院片区服务人口数"
                        need_service_people_nums = gr.Textbox(label="服务人口数", lines=1,
                                                              placeholder=placeholder_serve_nums)

                    with gr.Column():
                        placeholder_need_patient_nums = "医院输入患者人数"
                        need_patient_nums = gr.Textbox(label="患者人数（非必需项）", lines=1,
                                                       placeholder=placeholder_need_patient_nums)

                    with gr.Column():
                        placeholder_outpatient_land_area = "医院门诊占地面积"
                        outpatient_land_area = gr.Textbox(label="医院门诊部占地面积", lines=1,
                                                          placeholder=placeholder_outpatient_land_area)

                gr.Markdown("## 🎶 科室配置文件修改：")
                gr.Markdown("### 无需删除类目，仅需修改权重值--若使用默认配置请选择--department_v3，修改时请使用记事本保存为utf-8编码")
                with gr.Row():
                    # 下拉框选择配置文件
                    with gr.Row():
                        depart_config_swap = gr.Dropdown(choices=department_config_list,
                                                         label="选择科室的配置文件")
                    # 上传的文件列表
                    with gr.Column():
                        # 下载科室配置文件
                        download_depart_config_csv = gr.DownloadButton("下载科室配置文件模板-department_v3",
                                                                       value=download_department_config_csv,
                                                                       label='科室配置文件模板下载')
                        # 上传修改后的配置文件--传入csv文件
                        new_depart_config_csv = gr.UploadButton("选择修改后的科室配置文件 --（csv文件）",
                                                                file_count="single",
                                                                file_types=["csv"],
                                                                )
                        depart_config_name = gr.Textbox(label="科室配置命名", lines=1)

                        depart_config_button = gr.Button("上传科室配置文件", variant="primary")

                    depart_config_button.click(upload_depart_file,
                                               inputs=[new_depart_config_csv,
                                                       depart_config_name,
                                                       depart_config_swap],

                                               outputs=[depart_config_swap]
                                               )

                gr.Markdown("## 🎶 房间配置文件修改：")
                gr.Markdown("### 默认配置文件--room_v3，修改后文件格式不可修改，请使用记事本保存为utf-8编码")
                with gr.Row():
                    # 下拉框配置文件
                    room_config_swap = gr.Dropdown(choices=room_config_list,
                                                   label="选择房间的配置文件")
                    with gr.Column():
                        # 下载房间的配置文件
                        download_room_config = gr.DownloadButton("下载房间配置文件模板-room_v3",
                                                                 value=download_room_config_zip,
                                                                 label='房间配置文件下载')
                        # 上传用户修改后的房间配置文件
                        new_room_config = gr.UploadButton("选择修改后的房间配置文件压缩包 --（zip文件）",
                                                          file_count="single",
                                                          file_types=["zip"],
                                                          )

                        room_config_name = gr.Textbox(label="房间配置命名", lines=1)

                        room_config_button = gr.Button("上传房间配置文件", variant="primary")

                        room_config_button.click(upload_room_file,
                                                 inputs=[new_room_config, room_config_name, room_config_swap],
                                                 outputs=[room_config_swap]
                                                 )

                # 医院门诊科室需求选项
                gr.Markdown("## ⭐ 选择门诊部需要的科室")
                with gr.Row():
                    # 医院门诊科室支持的选项配置
                    required_depart_list = ["gynecology", "obstetrics", "pediatrics", "tcm", "endocrine", "hematology",
                                            "immuno_rheumatology",
                                            "infectious", "general_sugery", "orthopedic",
                                            "cardiovascular_center",
                                            "respiratory_center", "digestive_center", "neurocerebrovascular_center",
                                            "tumor_center",
                                            "urology_nephrology_center",
                                            "stomatology", "dermatology", "physiotherapy", "aesthetic", "counseling",
                                            "ophthalmology",
                                            "ent", "operating",
                                            "opd_hall", "opd_pharmacy", "opd_assay", "opd_treatment_room", "opd_office"]

                    with gr.Column():
                        check_required_depart = gr.CheckboxGroup(required_depart_list, label="门诊科室", info="选择需要的门诊科室")

                # 剩余面积分配方式
                gr.Markdown("## ⭐ 剩余面积分配方式")
                gr.Markdown("### method1：剩余面积用于增加科室房间数量, method2：剩余面积用于增加指定部分面积, method3：剩余面积不分配")
                with gr.Row():
                    # 下拉框配置文件
                    area_config_list = ["method1", "method2", "method3"]
                    area_config_swap = gr.Dropdown(choices=area_config_list,
                                                   label="选择剩余面积分配方式")

                gr.Markdown("### 若选择method2请填写需要增加的面积文件[输入房间名称及该房间在原始基础上增加的面积，"
                            "输入房间名称及该房间在原始基础上增加的数量，输入科室名称及科室走廊的新宽度（原有宽度设定为2.4m）]")
                with gr.Row():
                    # method2的配置文件
                    method2_example = """
                    {"input_depart_room_name_add_area": ["depart/room/area","depart/room/area"],
                    "input_depart_room_nums_add_count": ["depart/room/3","depart/room/3"],
                    "input_depart_corridor_width": ["depart/3","depart/3"]}
                    """
                    method2_example = gr.Textbox(value=method2_example, label="method2配置文件输入格式示例", lines=3)

                    method2_config = gr.Textbox(label="method2配置文件输入", lines=3)

                # 生成医院门诊任务按钮
                with gr.Row():
                    with gr.Column():
                        brief_create_button = gr.Button("生成医院门诊建筑任务书", variant="primary")

                # 下载已经生成的任务书
                with gr.Row():
                    with gr.Column():
                        # 定义输入和输出
                        outputs = gr.components.File(label="下载文件", show_label=False, )
                        interface = gr.Interface(fn=download_file, inputs=[name], outputs=outputs,
                                                 description="下载已经生成的任务书csv文件进行查看"
                                                 )

            outpaint_brief_gen_click = brief_create_button.click(
                generate_outpatient_brief_webui,
                inputs=[name, need_bed_nums, need_service_people_nums,
                        need_patient_nums, outpatient_land_area,
                        depart_config_swap, room_config_swap,
                        area_config_swap,
                        check_required_depart,
                        method2_config]
            )


            # 加入登录密码
            barkgui.queue().launch(show_error=True, server_name=args.host, server_port=args.port, share=True,
                                   # auth=("opd", "opd")
                                   # auth=("quyongbo", "quyongbo")
                                   )
