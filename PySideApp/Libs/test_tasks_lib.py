import time
from abc import abstractmethod
from enum import auto, Enum

import pandas as pd

class ParamType(Enum):
    int = auto()
    float = auto()
    xy_point = auto()
    xyz_point = auto()
    z = auto()


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
    def __init__(self, param_name:str, param_value:float|int, unit='', data_type:ParamType=ParamType.float):
        """
        data_type可选值见TestParamInputType定义
        """
        self.name = param_name
        self.value = param_value
        self.unit = unit
        self.type = data_type

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
            note: str | None = None,
            timestamp: float | None = None,
    ):
        self.id = uuid
        self.create_timestamp = timestamp
        self.name = task_name
        self.type = task_type
        self.input_param_list = input_param_list
        self.step_list = step_list
        self.org_dataframe: pd.DataFrame|None = None
        self.note = note
        self.current_step = 0

    def next_step(self):
        self._step_ctrller('next')

    def prev_step(self):
        self._step_ctrller('prev')

    def redo_step(self):
        self._step_ctrller('redo')

    def _step_ctrller(self, order:str):
        if order in ['next']:
            self.step_list[self.current_step].set_step_timestamp_end(time.time())
            self.current_step += 1
            self.step_list[self.current_step].set_step_timestamp_start(time.time())
        elif order in ['prev']:
            self.step_list[self.current_step].set_step_timestamp_start(None)
            self.step_list[self.current_step].set_step_timestamp_end(None)
            self.current_step -= 1
            self.step_list[self.current_step].set_step_timestamp_start(time.time())
            self.step_list[self.current_step].set_step_timestamp_end(None)
        elif order in ['redo']:
            self.step_list[self.current_step].set_step_timestamp_start(time.time())
            self.step_list[self.current_step].set_step_timestamp_end(None)

    def get_steps(self):
        prev_able = True
        next_able = True
        if len(self.step_list) <= self.current_step+1:
            next_able = False
        if self.current_step == 0:
            prev_able = False
        return self.step_list[self.current_step], next_able, prev_able

class TestModule:
    def __init__(
            self,
            name:str,
            search_keywords:list[str],
            test_task:TestTask|None=None,
            test_type:str='未分类',
            icon:str=u"folder",  # 默认使用qt内置folder标志
    ):
        self.name = name
        self.test_type = test_type
        self.search_keywords = search_keywords
        self.test_task = test_task
        self.icon = icon

    @abstractmethod
    def get_input_list(self) -> list[TestParamInput]:
        """
        定义计算输入参数
        """
        pass

    @abstractmethod
    def get_step_list(self) -> list[TestStep]:
        """
        定义检测步骤
        """
        pass

    def init_test_task(self, uuid: int, input_param_list: list[TestParamInput], note: str | None = None, ):
        """
        初始化测试任务
        """
        self.test_task = TestTask(
            uuid=uuid,
            timestamp=time.time(),
            task_name=self.name,
            task_type=self.test_type,
            input_param_list=input_param_list,
            step_list=self.get_step_list(),
            note=note,
        )

    def calculate(self, data: pd.DataFrame):
        """
        通用计算触发入口
        """
        self._validate_data()
        self.test_task.org_dataframe = data
        return self._perform_calculation(data)

    def _validate_data(self):
        for step in self.test_task.step_list:
            if step.need and (step.timestamp_start is None or step.timestamp_end is None):
                raise ValueError('关键步骤缺失时间戳数据')

    @abstractmethod
    def _perform_calculation(self, data: pd.DataFrame) -> tuple[str, str]:
        pass

    def export_test_task(self):
        """
        导出任务
        """
        return self.test_task