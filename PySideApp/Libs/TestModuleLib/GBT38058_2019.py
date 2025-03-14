import pandas as pd
from PySideApp.Libs.test_tasks_lib import TestModule, TestParamInput, TestStep

TYPE = 'GB/T 38058-2019 民用多旋翼无人机系统试验方法'

class T6_4_2(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.4.2 最大作业半径',
            search_keywords=['38058', '作业半径', '642'],
        )
        # 轮数指示
        self.round_count = 3

    def init_test_task(self, input_param_list, uuid: int, note: str | None = None):
        # 在创建 test_task 之前,先获取输入的轮数
        for param in input_param_list:
            if param.name == '测试轮数 等于':
                self.round_count = int(param.value)
                break

        super().init_test_task(uuid, input_param_list, note)

    def get_input_list(self):
        return [
            TestParamInput('测试轮数 等于', self.round_count, '轮', data_type='int'),
            TestParamInput('半径 大于', 20.0, 'm')
        ]

    def get_step_list(self):
        list_temp = [
            TestStep('无人机起飞'),
            TestStep('飞行到A点后，点击下一步'),
        ]
        for i in range(self.round_count):
            list_temp.extend([
                    TestStep(f'第{i + 1}/{self.round_count}轮：直线平飞飞行到B点，到达B点后，点击下一步', True),
                    TestStep(f'第{i + 1}/{self.round_count}轮,直线平飞向A点返航，到达A点后或确认无法回到A点后，点击下一步', True),
                ])
        list_temp.extend([
                TestStep('记录完成。'),
            ])
        return list_temp

    def _perform_calculation(self, data:pd.DataFrame):
        inputs = []
        for param in self.test_task.input_param_list:
            inputs.append(param.value)
        for step in self.test_task.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e
                else:
                    """
                    从dataframe截取指定时间戳之间的数据
                    """
        self.test_task.org_dataframe = data
        return '1212.4', '0.05'

class T6_4_3(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.4.3 最大飞行海拔高度',
            search_keywords=['38058', '海拔高度', '高度', '海拔', '643'],
        )

    def init_test_task(self, input_param_list, uuid: int, note: str | None = None):
        # 先取得输入参数的值
        for param in input_param_list:
            if param.name == '海拔高度 大于':
                self.height = float(param.value)
                break

        super().init_test_task(uuid, input_param_list, note)

    def get_input_list(self):
        return [
            TestParamInput('海拔高度 大于', 50.0, 'm')
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞'),
            TestStep(f'逐渐抬高无人机高度，确认无人机已经到达海拔高度{self.height}米'),
            TestStep('操作无人机前飞、后飞、侧飞、转向，并悬停3min', True),
            TestStep('记录完成。'),
        ]

    def _perform_calculation(self, data:pd.DataFrame):
        inputs = []
        for param in self.test_task.input_param_list:
            inputs.append(param.value)
        for step in self.test_task.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e
                else:
                    """
                    从dataframe截取指定时间戳之间的数据
                    """
        self.test_task.org_dataframe = data
        return '1212.4', '0.05'

class T6_4_4(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.4.4 最大平飞速度',
            search_keywords=['38058', '平飞', '速度', '644'],
        )
        # 轮数指示
        self.round_count = 2

    def get_input_list(self):
        return [
            # TestParamInput('速度 大于', 11.1, 'm/s')
        ]

    def get_step_list(self):
        list_temp = [
            TestStep('无人机起飞到空旷处，准备进行水平加速飞行'),
        ]
        for i in range(self.round_count):
            round_pre = f"第{i + 1}/{self.round_count}轮："
            list_temp.extend([
                TestStep(f'{round_pre}操作无人机进行水平直线加速飞行，确认达到最大速度飞行的稳定状态后，点击下一步'),
                TestStep(f'{round_pre}保持最大速度飞行5秒后，点击下一步', True),
                TestStep(f'{round_pre}无人机转向180°，确保方向与上一步相反'),
                TestStep(f'{round_pre}操作无人机进行水平直线加速飞行，确认达到最大速度飞行的稳定状态后，点击下一步'),
                TestStep(f'{round_pre}保持最大速度飞行5秒后，点击下一步', True),
            ])
        list_temp.extend([
            TestStep('记录完成。'),
        ])

        return list_temp

    def _perform_calculation(self, data:pd.DataFrame):
        inputs = []
        for param in self.test_task.input_param_list:
            inputs.append(param.value)
        for step in self.test_task.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e
                else:
                    """
                    从dataframe截取指定时间戳之间的数据
                    """
        self.test_task.org_dataframe = data
        return '1212.4', '0.05'

class T6_4_5(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.4.5 最大爬升速率',
            search_keywords=['38058', '爬升速率', '爬升速度', '爬升', '爬升率', '645'],
        )
        # 轮数指示
        self.round_count = 3

    def get_input_list(self):
        return [
            # TestParamInput('爬升率 大于', 5.0, 'm/s')
        ]

    def get_step_list(self):
        list_temp = [
            TestStep('无人机起飞，点击下一步'),
        ]
        for i in range(self.round_count):
            round_pre = f"第{i + 1}/{self.round_count}轮："
            list_temp.extend([
                TestStep(f'{round_pre}无人机加速爬升，确认到达最大爬升速度后，点击下一步'),
                TestStep(f'{round_pre}保持最大爬升速度飞行5秒后，点击下一步', True),
                TestStep(f'{round_pre}无人机回到起点准备下一轮测试或完成测试'),
            ])
        list_temp.extend([
            TestStep('记录完成。'),
        ])

        return list_temp

    def _perform_calculation(self, data:pd.DataFrame):
        inputs = []
        for param in self.test_task.input_param_list:
            inputs.append(param.value)
        for step in self.test_task.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e
                else:
                    """
                    从dataframe截取指定时间戳之间的数据
                    """
        self.test_task.org_dataframe = data
        return '1212.4', '0.05'

class T6_4_6(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.4.6 高度保持性能',
            search_keywords=['38058', '高度', '高度保持', '646'],
        )
        self.height_list = []

    def init_test_task(self, input_param_list, uuid: int, note: str | None = None):
        # 先取得输入参数的值
        for param in input_param_list:
            if param.name == '预设高度H1':
                self.height_list.append(float(param.value))
            elif param.name == '预设高度H2':
                self.height_list.append(float(param.value))
            elif param.name == '预设高度H3':
                self.height_list.append(float(param.value))
                break

        super().init_test_task(uuid, input_param_list, note)


    def get_input_list(self):
        return [
            # TestParamInput('定高误差 小于', 5.0, 'm'),
            # TestParamInput('定高波动大小 小于', 11.1, 'm'),
            TestParamInput('预设高度H1', 7.0, 'm'),
            TestParamInput('预设高度H2', 14.0, 'm'),
            TestParamInput('预设高度H3', 23.0, 'm'),
            TestParamInput('v1', 2.0, 'm/s'),
            TestParamInput('v2', 2.4, 'm/s'),
            TestParamInput('v3', 2.8, 'm/s'),
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞'),
            TestStep(f'第一轮：飞行到预设高度{self.height_list[1]}米，平稳后点击下一步'),
            TestStep('第一轮：以当前高度水平飞行30s', True),
            TestStep(f'第二轮：飞行到预设高度{self.height_list[1]}米，平稳后点击下一步'),
            TestStep('第二轮：以当前高度水平飞行30s', True),
            TestStep(f'第三轮：飞行到预设高度{self.height_list[1]}米，平稳后点击下一步'),
            TestStep('第三轮：以当前高度水平飞行30s', True),
            TestStep('记录完成。'),
        ]

    def _perform_calculation(self, data:pd.DataFrame):
        inputs = []
        for param in self.test_task.input_param_list:
            inputs.append(param.value)
        for step in self.test_task.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e
                else:
                    """
                    从dataframe截取指定时间戳之间的数据
                    """
        self.test_task.org_dataframe = data
        return '1212.4', '0.05'

class T6_4_7(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.4.7 速度保持性能',
            search_keywords=['38058', '速度', '速度保持', '647'],
        )
        self.height_list = []

    def init_test_task(self, input_param_list, uuid: int, note: str | None = None):
        # 先取得输入参数的值
        for param in input_param_list:
            if param.name == '预设高度H1':
                self.height_list.append(float(param.value))
            elif param.name == '预设高度H2':
                self.height_list.append(float(param.value))
            elif param.name == '预设高度H3':
                self.height_list.append(float(param.value))
                break

        super().init_test_task(uuid, input_param_list, note)

    def get_input_list(self):
        return [
            TestParamInput('预设高度H1', 7.0, 'm'),
            TestParamInput('预设高度H2', 14.0, 'm'),
            TestParamInput('预设高度H3', 23.0, 'm'),
            TestParamInput('v1', 2.0, 'm/s'),
            TestParamInput('v2', 2.4, 'm/s'),
            TestParamInput('v3', 2.8, 'm/s'),
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞'),
            TestStep(f'第一轮：飞行到预设高度{self.height_list[1]}米，平稳后点击下一步'),
            TestStep('第一轮：以当前高度水平飞行30s', True),
            TestStep(f'第二轮：飞行到预设高度{self.height_list[1]}米，平稳后点击下一步'),
            TestStep('第二轮：以当前高度水平飞行30s', True),
            TestStep(f'第三轮：飞行到预设高度{self.height_list[1]}米，平稳后点击下一步'),
            TestStep('第三轮：以当前高度水平飞行30s', True),
            TestStep('记录完成。'),
        ]

    def _perform_calculation(self, data:pd.DataFrame):
        inputs = []
        for param in self.test_task.input_param_list:
            inputs.append(param.value)
        for step in self.test_task.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e
                else:
                    """
                    从dataframe截取指定时间戳之间的数据
                    """
        self.test_task.org_dataframe = data
        return '1212.4', '0.05'

class T6_4_9(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.4.9 定点悬停',
            search_keywords=['38058', '定点', '悬停', '649'],
        )
        # 轮数指示
        self.round_count = 5

    def init_test_task(self, input_param_list, uuid: int, note: str | None = None):
        # 先取得输入参数的值
        for param in input_param_list:
            if param.name == '悬停高度 等于':
                self.height = float(param.value)
                break

        super().init_test_task(uuid, input_param_list, note)

    def get_input_list(self):
        return [
            TestParamInput('悬停高度 等于', 10.0, 'm'),
        ]

    def get_step_list(self):
        list_temp = [
            TestStep(f'无人机起飞到离地{self.height}米处'),
        ]
        for i in range(self.round_count):
            round_pre = f"第{i + 1}/{self.round_count}轮："
            list_temp.extend([
                TestStep(f'{round_pre}移动到悬停点{i + 1}/{self.round_count}，启动悬停功能后，点击下一步'),
                TestStep(f'{round_pre}保持3分钟后，点击下一步', True),
            ])
        list_temp.extend([
            TestStep('记录完成。'),
        ])

        return list_temp

    def _perform_calculation(self, data:pd.DataFrame):
        inputs = []
        for param in self.test_task.input_param_list:
            inputs.append(param.value)
        for step in self.test_task.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e
                else:
                    """
                    从dataframe截取指定时间戳之间的数据
                    """
        self.test_task.org_dataframe = data
        return '1212.4', '0.05'

class T6_4_10(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.4.10 定位导航',
            search_keywords=['38058', '定位', '导航', '定位导航', '6410'],
        )

    def get_input_list(self):
        return [
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞，准备飞行，点击下一步开始采集'),
            TestStep('按照xy平面非重合轨迹飞行完毕后，下一步', True),
            TestStep('记录完成。'),
        ]

    def _perform_calculation(self, data:pd.DataFrame):
        inputs = []
        for param in self.test_task.input_param_list:
            inputs.append(param.value)
        for step in self.test_task.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e
                else:
                    """
                    从dataframe截取指定时间戳之间的数据
                    """
        self.test_task.org_dataframe = data
        return '1212.4', '0.05'

class T6_4_11(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.4.11 航迹精度',
            search_keywords=['38058', '高度', '高度保持', '6411'],
        )

    def get_input_list(self):
        return [
            TestParamInput('轨迹起点 经 纬', 0.0, data_type="xy_point"),
            TestParamInput('轨迹终点 经 纬', 0.0, data_type="xy_point"),
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞，准备飞行，点击下一步开始采集'),
            TestStep('开始按照预定直线轨迹飞行，完成后下一步', True),
            TestStep('记录完成。'),
        ]

    def _perform_calculation(self, data:pd.DataFrame):
        inputs = []
        for param in self.test_task.input_param_list:
            inputs.append(param.value)
        for step in self.test_task.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e
                else:
                    """
                    从dataframe截取指定时间戳之间的数据
                    """
        self.test_task.org_dataframe = data
        return '1212.4', '0.05'

# class T6_6_1(TestModule):
#     def __init__(self):
#         super().__init__(
#             test_type=TYPE,
#             name='6.6.1 静态姿态精度',
#             search_keywords=['38058', '高度', '高度保持', '646'],
#         )
#
#     def get_input_list(self):
#         return [
#             TestParamInput('定高误差 小于', 5.0, 'm'),
#             TestParamInput('定高波动大小 小于', 11.1, 'm'),
#             TestParamInput('预设高度H1', 7.0, 'm'),
#             TestParamInput('预设高度H2', 14.0, 'm'),
#             TestParamInput('预设高度H3', 23.0, 'm'),
#         ]
#
#     def get_step_list(self):
#         return [
#             TestStep('无人机起飞'),
#             TestStep('飞行到预设高度H1，平稳后点击下一步'),
#             TestStep('第一轮：以当前高度水平飞行30s', True),
#             TestStep('飞行到预设高度H2，平稳后点击下一步'),
#             TestStep('第二轮：以当前高度水平飞行30s', True),
#             TestStep('飞行到预设高度H3，平稳后点击下一步'),
#             TestStep('第三轮：以当前高度水平飞行30s', True),
#             TestStep('记录完成。'),
#         ]
#
#     def _perform_calculation(self, data:pd.DataFrame):
#         inputs = []
#         for param in self.test_task.input_param_list:
#             inputs.append(param.value)
#         for step in self.test_task.step_list:
#             if step.need:
#                 if step.timestamp_start is None or step.timestamp_end is None:
#                     e = '关键的步骤缺失时间戳数据'
#                     raise e
#                 else:
#                     """
#                     从dataframe截取指定时间戳之间的数据
#                     """
#         self.test_task.org_dataframe = data
#         return '1212.4', '0.05'

# class T6_6_2(TestModule):
#     def __init__(self):
#         super().__init__(
#             test_type='GB/T 38058-2019 民用多旋翼无人机系统试验方法',
#             name='6.4.6 高度保持性能',
#             search_keywords=['38058', '高度', '高度保持', '646'],
#         )
#
#     def get_input_list(self):
#         return [
#             TestParamInput('定高误差 小于', 5.0, 'm'),
#             TestParamInput('定高波动大小 小于', 11.1, 'm'),
#             TestParamInput('预设高度H1', 7.0, 'm'),
#             TestParamInput('预设高度H2', 14.0, 'm'),
#             TestParamInput('预设高度H3', 23.0, 'm'),
#         ]
#
#     def get_step_list(self):
#         return [
#             TestStep('无人机起飞'),
#             TestStep('飞行到预设高度H1，平稳后点击下一步'),
#             TestStep('第一轮：以当前高度水平飞行30s', True),
#             TestStep('飞行到预设高度H2，平稳后点击下一步'),
#             TestStep('第二轮：以当前高度水平飞行30s', True),
#             TestStep('飞行到预设高度H3，平稳后点击下一步'),
#             TestStep('第三轮：以当前高度水平飞行30s', True),
#             TestStep('记录完成。'),
#         ]
#
#     def _perform_calculation(self, data:pd.DataFrame):
#         inputs = []
#         for param in self.test_task.input_param_list:
#             inputs.append(param.value)
#         for step in self.test_task.step_list:
#             if step.need:
#                 if step.timestamp_start is None or step.timestamp_end is None:
#                     e = '关键的步骤缺失时间戳数据'
#                     raise e
#                 else:
#                     """
#                     从dataframe截取指定时间戳之间的数据
#                     """
#         self.test_task.org_dataframe = data
#         return '1212.4', '0.05'

class T6_7_1(TestModule):
    def __init__(self):
        super().__init__(
            test_type='GB/T 38058-2019 民用多旋翼无人机系统试验方法',
            name='6.7.1 遥控遥测距离',
            search_keywords=['38058', '遥控', '遥测', '671'],
        )
        # 轮数指示
        self.round_count = 5

    def get_input_list(self):
        return [
            TestParamInput('坐标零点', 0.0, data_type="xyz_point"),
        ]

    def get_step_list(self):
        list_temp = [
            TestStep('无人机放置于坐标零点起飞，下一步'),
        ]
        for i in range(self.round_count):
            round_pre = f"第{i + 1}/{self.round_count}轮："
            list_temp.extend([
                TestStep(f'{round_pre}从零点开始直线低空飞行，确认到无人机系统提示功能异常后，点击下一步', True),
                TestStep(f'{round_pre}返回零点后，点击下一步'),
            ])
        list_temp.extend([
            TestStep('记录完成。'),
        ])
        return list_temp

    def _perform_calculation(self, data:pd.DataFrame):
        inputs = []
        for param in self.test_task.input_param_list:
            inputs.append(param.value)
        for step in self.test_task.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e
                else:
                    """
                    从dataframe截取指定时间戳之间的数据
                    """
        self.test_task.org_dataframe = data
        return '1212.4', '0.05'

class T6_7_2(TestModule):
    def __init__(self):
        super().__init__(
            test_type='GB/T 38058-2019 民用多旋翼无人机系统试验方法',
            name='6.7.2 信息传输距离',
            search_keywords=['38058', '信息传输', '传输', '672'],
        )
        # 轮数指示
        self.round_count = 5

    def get_input_list(self):
        return [
            TestParamInput('坐标零点', 0.0, data_type="xy_point"),
        ]

    def get_step_list(self):
        list_temp = [
            TestStep('无人机放置于坐标零点起飞，下一步'),
        ]
        for i in range(self.round_count):
            round_pre = f"第{i + 1}/{self.round_count}轮："
            list_temp.extend([
                TestStep(f'{round_pre}从零点开始直线低空飞行，确认到无人机数据传输质量出问题后，点击下一步', True),
                TestStep(f'{round_pre}返回零点后，点击下一步'),
            ])
        list_temp.extend([
            TestStep('记录完成。'),
        ])
        return list_temp

    def _perform_calculation(self, data:pd.DataFrame):
        inputs = []
        for param in self.test_task.input_param_list:
            inputs.append(param.value)
        for step in self.test_task.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e
                else:
                    """
                    从dataframe截取指定时间戳之间的数据
                    """
        self.test_task.org_dataframe = data
        return '1212.4', '0.05'
