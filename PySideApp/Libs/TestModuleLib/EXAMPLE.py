import pandas as pd
from PySideApp.Libs.test_tasks_lib import TestModule, TestParamInput, TestStep
TYPE = "DEBUG"


class TEST(TestModule):
    def __init__(self):
        super().__init__(
            test_type=TYPE,
            name='测试',
            search_keywords=['DEBUG', ],
        )
        # 轮数指示
        self.round_count = 5

    def init_test_task(self, input_param_list, uuid: int, note: str | None = None):
        # 先取得输入参数的值
        for param in input_param_list:
            if param.name == '普通参数':
                self.param1 = float(param.value)  # 取某变量到步骤文本中
                break

        super().init_test_task(uuid, input_param_list, note)

    def get_input_list(self):
        return [
            TestParamInput('xy点 经 纬', 0.0, data_type="xy_point"),
            TestParamInput('xyz点 经 纬', 0.0, data_type="xyz_point"),
            TestParamInput('z高度', 0.0, data_type="z"),
            TestParamInput('整数参数', 1, data_type="int", unit="次"),
            TestParamInput('普通参数', 20.0, unit="米"),
            TestParamInput('轮数', 5, data_type="int", unit="轮"),
        ]

    def get_step_list(self):
        list_temp = [
            TestStep('测试开始：纯文本步骤'),
            TestStep(f'取参数步骤：{self.param1}'),
        ]
        for i in range(self.round_count):
            round_pre = f"第{i + 1}/{self.round_count}轮："
            list_temp.extend([
                TestStep(f'{round_pre}步骤'),
                TestStep(f'{round_pre}需要取值的步骤', True),
            ])
        list_temp.extend([
            TestStep('记录完成。'),
        ])

        return list_temp

    def _perform_calculation(self, data: pd.DataFrame):
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
