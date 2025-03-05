import pandas as pd
from PySideApp.Libs.test_tasks_lib import TestModule, TestParamInput, TestStep

TYPE = 'DL/T 1578-2021 架空电力线路多旋翼无人机巡检系统'

class T6_3_2_4(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.3.2.4 导航定位偏差实验',
            search_keywords=['1578', '定位偏差', '6324'],
        )

    def get_input_list(self):
        return [
            TestParamInput('半径 大于', 20.0, 'm')
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞，飞行到大约10米高度'),
            TestStep('第一轮：飞行到起点悬停，记为A1点'),
            TestStep('以5m/s的速度操作无人机向设定的飞行半径飞行，确认飞机已经到达指定的飞行半径，记为B1点', True),
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
