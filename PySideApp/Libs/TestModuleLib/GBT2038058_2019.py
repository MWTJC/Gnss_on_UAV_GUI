import pandas as pd
from PySideApp.Libs.test_tasks_lib import TestModule, TestParamInput, TestStep


class T6_4_2(TestModule):
    def __init__(self):
        super().__init__(
            test_type='GB/T 38058-2019 民用多旋翼无人机系统试验方法',
            name='6.4.2 最大作业半径',
            search_keywords=['38058', '作业半径', '642'],
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

class T6_4_3(TestModule):
    def __init__(self):
        super().__init__(
            test_type='GB/T 38058-2019 民用多旋翼无人机系统试验方法',
            name='6.4.3 最大飞行海拔高度',
            search_keywords=['38058', '海拔高度', '高度', '海拔', '643'],
        )

    def get_input_list(self):
        return [
            TestParamInput('海拔高度 大于', 50.0, 'm')
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞'),
            TestStep('逐渐抬高无人机高度，确认无人机已经到达最大飞行高度'),
            TestStep('操作无人机前飞、后飞、侧飞、转向，并悬停3min', True),
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

class T6_4_4(TestModule):
    def __init__(self):
        super().__init__(
            test_type='GB/T 38058-2019 民用多旋翼无人机系统试验方法',
            name='6.4.4 最大平飞速度',
            search_keywords=['38058', '平飞', '速度', '644'],
        )

    def get_input_list(self):
        return [
            TestParamInput('速度 大于', 11.1, 'm/s')
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞'),
            TestStep('飞行到大约100m ± 10m米高度'),
            TestStep('操作无人机进行水平直线加速飞行，达到最大速度飞行的稳定状态后点击下一步'),
            TestStep('第一轮：无人机按最大速度飞行，飞行航段达到500m后，点击下一步', True),
            TestStep('减速重整姿态，向相反方向加速，达到最大速度飞行的稳定状态后点击下一步'),
            TestStep('第二轮：无人机按最大速度飞行，飞行航段达到500m后，点击下一步', True),
            TestStep('减速重整姿态，向相反方向加速，达到最大速度飞行的稳定状态后点击下一步'),
            TestStep('第三轮：无人机按最大速度飞行，飞行航段达到500m后，点击下一步', True),
            TestStep('减速重整姿态，向相反方向加速，达到最大速度飞行的稳定状态后点击下一步'),
            TestStep('第四轮：无人机按最大速度飞行，飞行航段达到500m后，点击下一步', True),
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

class T6_4_5(TestModule):
    def __init__(self):
        super().__init__(
            test_type='GB/T 38058-2019 民用多旋翼无人机系统试验方法',
            name='6.4.5 最大爬升速率',
            search_keywords=['38058', '爬升速率', '爬升速度', '爬升', '爬升率', '645'],
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

class T6_4_6(TestModule):
    def __init__(self):
        super().__init__(
            test_type='GB/T 38058-2019 民用多旋翼无人机系统试验方法',
            name='6.4.6 高度保持性能',
            search_keywords=['38058', '高度', '高度保持', '646'],
        )

    def get_input_list(self):
        return [
            TestParamInput('定高误差 小于', 5.0, 'm'),
            TestParamInput('定高波动大小 小于', 11.1, 'm'),
            TestParamInput('预设高度H1', 7.0, 'm'),
            TestParamInput('预设高度H2', 14.0, 'm'),
            TestParamInput('预设高度H3', 23.0, 'm'),
        ]

    def get_step_list(self):
        return [
            TestStep('无人机起飞'),
            TestStep('飞行到预设高度H1，平稳后点击下一步'),
            TestStep('第一轮：以当前高度水平飞行30s', True),
            TestStep('飞行到预设高度H2，平稳后点击下一步'),
            TestStep('第二轮：以当前高度水平飞行30s', True),
            TestStep('飞行到预设高度H3，平稳后点击下一步'),
            TestStep('第三轮：以当前高度水平飞行30s', True),
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
