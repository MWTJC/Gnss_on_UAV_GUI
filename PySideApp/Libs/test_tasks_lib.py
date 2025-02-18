import time
import pandas as pd


class TestStep:
    def __init__(self, describe:str, essential=False):
        self.describe = describe
        self.timestamp_start = None
        self.timestamp_end = None
        self.need = essential

    def set_step_timestamp_start(self, timestamp_start):
        self.timestamp_start = timestamp_start

    def set_step_timestamp_end(self, timestamp_end):
        self.timestamp_end = timestamp_end

class TestParamInput:
    def __init__(self, param_name:str, param_value:float, unit=''):
        self.name = param_name
        self.value = param_value
        self.unit = unit

class TestTask:
    def __init__(
            self,
            uuid: int,
            input_param_list: list[TestParamInput],
            step_list: list[TestStep],
            task_name='未定义的检测项目',
            icon=None,
    ):
        self.id = uuid
        self.name = task_name
        self.icon = icon
        self.input_param_list = input_param_list
        self.step_list = step_list

        self.current_step = 0

    def step_ctrller(self, order:str):
        if order in ['next']:
            self.step_list[self.current_step].set_step_timestamp_end(time.time())
            self.current_step += 1
            self.step_list[self.current_step].set_step_timestamp_start(time.time())
        elif order in ['redo']:
            self.step_list[self.current_step].set_step_timestamp_start(time.time())
            self.step_list[self.current_step].set_step_timestamp_end(None)

    def calculate(self, data:pd.DataFrame):
        for step in self.step_list:
            if step.need:
                if step.timestamp_start is None or step.timestamp_end is None:
                    e = '关键的步骤缺失时间戳数据'
                    raise e



if __name__ == '__main__':
    input_list_demo = [
        TestParamInput('航向精度 小于', 1.0, '°')
    ]
    step_list_demo = [
        TestStep('将无人机测试设备上电'),
        TestStep('无人机起飞，飞行到大约3米高度'),
        TestStep('预设航线采集：无人机悬停至基准点'),
        TestStep('无人机在目标点悬停', True),
        TestStep('操控无人机回到起点，飞行到大约3米高度'),
        TestStep('第1次测试：无人机飞行至基准点，悬停'),
        TestStep('无人机飞行至目标点，悬停', True),
        TestStep('操控无人机回到起点，飞行到大约3米高度'),
        TestStep('第2次测试：无人机飞行至基准点，悬停'),
        TestStep('无人机飞行至目标点，悬停', True),
        TestStep('操控无人机回到起点，飞行到大约3米高度'),
        TestStep('第3次测试：无人机飞行至基准点，悬停'),
        TestStep('无人机飞行至目标点，悬停', True),
        TestStep('完成航向精度测试'),
    ]
    task1 = TestTask(
        uuid=123456,
        task_name='航向精度测试',
        input_param_list=input_list_demo,
        step_list=step_list_demo,
    )