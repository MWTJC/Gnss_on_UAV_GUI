import pandas as pd
from PySideApp.Libs.test_tasks_lib import TestModule, TestParamInput, TestStep

TYPE = 'DL/T 1578-2021 架空电力线路多旋翼无人机巡检系统'

class T1578_6327(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='6.3.2.7 惯性飞行距离试验',
            search_keywords=['1578', '惯性', '6327'],
        )

    def get_input_list(self):
        return [
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞，按照标准描述设定航线，以2m/s飞行，下一步'),
            TestStep('请断开所有飞行指令，使无人机仅在惯性作用下减速滑行至停止，无人机停止后点击下一步', True),
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
