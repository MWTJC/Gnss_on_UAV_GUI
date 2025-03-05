import pandas as pd
from PySideApp.Libs.test_tasks_lib import TestModule, TestParamInput, TestStep

TYPE = 'GA/T 1411.3/4-2017 警用无人驾驶航空器系统 第三部分、第四部分'

class T6_2_1(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.2.1 有效载荷系数检验',
            search_keywords=['1411', '载荷', '624'],
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
