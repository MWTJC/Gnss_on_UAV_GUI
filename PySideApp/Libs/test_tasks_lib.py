class TestPlayer:
    def __init__(self):
        pass

class TestTask:
    def __init__(self):
        self.id = 'undefined'
        self.name = '未定义的检测项目'
        self.icon = None
        self.input_param_list:list[TestParamInput] = []
        self.procedure_list:list[TestStep] = []

class TestStep:
    def __init__(self):
        self.text = ''

class TestParamInput:
    def __init__(self):
        self.text = ''
        self.value = 0.00
        self.unit = ''