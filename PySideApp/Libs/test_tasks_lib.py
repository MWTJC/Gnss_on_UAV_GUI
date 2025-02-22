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

    def set_value(self, new_value):
        self.value = new_value

class TestTask:
    def __init__(
            self,
            uuid: int,
            input_param_list: list[TestParamInput],
            step_list: list[TestStep],
            task_type='未定义的检测类别',
            task_name='未定义的检测项目',
            icon=None,
            note: str | None = None,
            timestamp: float | None = None,
    ):
        self.id = uuid
        self.create_timestamp = timestamp
        self.name = task_name
        self.type = task_type
        self.icon = icon
        self.input_param_list = input_param_list
        self.step_list = step_list
        self.org_dataframe: pd.DataFrame|None = None
        self.note = note
        self.current_step = 0

    def next_step(self):
        self._step_ctrller('next')

    def redo_step(self):
        self._step_ctrller('redo')

    def _step_ctrller(self, order:str):
        if order in ['next']:
            self.step_list[self.current_step].set_step_timestamp_end(time.time())
            self.current_step += 1
            self.step_list[self.current_step].set_step_timestamp_start(time.time())
        elif order in ['redo']:
            self.step_list[self.current_step].set_step_timestamp_start(time.time())
            self.step_list[self.current_step].set_step_timestamp_end(None)

    def get_steps(self):
        if len(self.step_list) <= self.current_step+1:
            return self.step_list[self.current_step], True
        else:
            return self.step_list[self.current_step], False