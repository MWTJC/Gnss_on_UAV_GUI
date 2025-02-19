import pandas as pd

from PySideApp.Libs.test_tasks_lib import TestTask, TestParamInput, TestStep


class TestModule:
    def __init__(self, name:str, search_keywords:list[str], test_task:TestTask|None=None, test_type:str='未分类', ):
        self.name = name
        self.test_type = test_type
        self.search_keywords = search_keywords
        self.test_task = test_task

    def export_test_task(self):
        return self.test_task


class GBT2038058_2019_6_4_5(TestModule):
    def __init__(self):
        super().__init__(
            test_type='GB/T 38058-2019 民用多旋翼无人机系统试验方法',
            name='6.4.5 最大爬升速率',
            search_keywords=['2038058', '爬升速率', '爬升速度', '爬升', '爬升率', '645'],
        )
    def init_test_task(self, uuid:int):
        input_list_demo = [
            TestParamInput('爬升率 大于', 5.0, 'm/s')
        ]
        step_list_demo = [
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
        task = TestTask(
            uuid=uuid,
            task_name=self.name,
            input_param_list=input_list_demo,
            step_list=step_list_demo,
        )
        self.test_task = task

    def calculate(self, data:pd.DataFrame):
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