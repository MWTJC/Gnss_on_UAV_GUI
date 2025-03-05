import pandas as pd
from PySideApp.Libs.test_tasks_lib import TestModule, TestParamInput, TestStep


class MaxHeight(TestModule):
    def __init__(self):
        super().__init__(
            test_type='基本',
            name='最大飞行高度',
            search_keywords=['高度', '高'],
        )

    def get_input_list(self):
        return [
            TestParamInput('高度 大于', 50.0, 'm')
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞，飞行到大约10米高度，悬停'),
            TestStep('开始逐渐抬高飞机高度，确认飞机已经到达最高飞行高度', True),
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
