import pandas as pd
from PySideApp.Libs.test_tasks_lib import TestModule, TestParamInput, TestStep
TYPE = "基本"

class MaxHeight(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='轨迹记录',
            search_keywords=['轨迹',],
        )

    def get_input_list(self):
        return [
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞，点击下一步开始轨迹记录'),
            TestStep('正在采集，完成则点击下一步', True),
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
