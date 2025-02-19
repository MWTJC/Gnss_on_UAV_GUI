import pandas as pd
from abc import abstractmethod
from PySideApp.Libs.test_tasks_lib import TestTask, TestParamInput, TestStep


class TestModule:
    def __init__(self, name:str, search_keywords:list[str], test_task:TestTask|None=None, test_type:str='未分类', ):
        self.name = name
        self.test_type = test_type
        self.search_keywords = search_keywords
        self.test_task = test_task

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

    def init_test_task(self, uuid: int, note: str | None = None):
        """
        初始化测试任务
        """
        self.test_task = TestTask(
            uuid=uuid,
            task_name=self.name,
            input_param_list=self.get_input_list(),
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


class GBT2038058_2019_6_4_5(TestModule):
    def __init__(self):
        super().__init__(
            test_type='GB/T 38058-2019 民用多旋翼无人机系统试验方法',
            name='6.4.5 最大爬升速率',
            search_keywords=['2038058', '爬升速率', '爬升速度', '爬升', '爬升率', '645'],
        )

    def get_input_list(self):
        return [
            TestParamInput('爬升率 大于', 5.0, 'm/s')
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞，飞行到大约3米高度'),
            TestStep('准备控制无人机以最大速度爬升，到爬升速度稳定后点击下一步开始测量'),
            TestStep('按照最大爬升速度爬升5s，第一次测量', True),
            TestStep('控制无人机回到起点'),
            TestStep('准备控制无人机以最大速度爬升，到爬升速度稳定后点击下一步开始测量'),
            TestStep('按照最大爬升速度爬升5s，第二次测量', True),
            TestStep('控制无人机回到起点'),
            TestStep('准备控制无人机以最大速度爬升，到爬升速度稳定后点击下一步开始测量'),
            TestStep('按照最大爬升速度爬升5s，第三次测量', True),
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


class GBT2038058_2019_6_4_2(TestModule):
    def __init__(self):
        super().__init__(
            test_type='GB/T 38058-2019 民用多旋翼无人机系统试验方法',
            name='6.4.2 最大作业半径',
            search_keywords=['2038058', '作业半径', '642'],
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
            TestStep('在B1点保证无人机电量大于满电量的10%，准备向A1点返航'),
            TestStep('开始返航，若电量不足无法继续返航，记为C1点', True),
            TestStep('第二轮：飞行到起点悬停，记为A2点'),
            TestStep('以5m/s的速度操作无人机向设定的飞行半径飞行，确认飞机已经到达指定的飞行半径，记为B2点', True),
            TestStep('在B2点保证无人机电量大于满电量的10%，准备向A2点返航'),
            TestStep('开始返航，若电量不足无法继续返航，记为C2点', True),
            TestStep('第三轮：飞行到起点悬停，记为A3点'),
            TestStep('以5m/s的速度操作无人机向设定的飞行半径飞行，确认飞机已经到达指定的飞行半径，记为B3点', True),
            TestStep('在B3点保证无人机电量大于满电量的10%，准备向A3点返航'),
            TestStep('开始返航，若电量不足无法继续返航，记为C3点', True),
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

class NormalTestMaxHeight(TestModule):
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


def get_all_test():
    test_list = []
    for name, obj in globals().items():
        if isinstance(obj, type) and issubclass(obj, TestModule) and obj != TestModule:
            instance = obj()
            test_list.append(instance)
    return test_list

if __name__ == "__main__":
    print(get_all_test())