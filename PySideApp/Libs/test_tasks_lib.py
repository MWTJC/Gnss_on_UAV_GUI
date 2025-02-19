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
        self.org_dataframe: pd.DataFrame|None = None

        self.current_step = 0

    def step_ctrller(self, order:str):
        if order in ['next']:
            self.step_list[self.current_step].set_step_timestamp_end(time.time())
            self.current_step += 1
            self.step_list[self.current_step].set_step_timestamp_start(time.time())
            return self.step_list[self.current_step].describe
        elif order in ['redo']:
            self.step_list[self.current_step].set_step_timestamp_start(time.time())
            self.step_list[self.current_step].set_step_timestamp_end(None)
            return True
