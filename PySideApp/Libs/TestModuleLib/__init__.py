from PySideApp.Libs.TestModuleLib.GBT38058_2019 import *
from PySideApp.Libs.TestModuleLib.DLT1578_2021 import *
from PySideApp.Libs.TestModuleLib.GAT1411_3_4_2017 import *
from PySideApp.Libs.TestModuleLib.GB42590_2023 import *
from PySideApp.Libs.TestModuleLib.Tools import *
from PySideApp.Libs.TestModuleLib.EXAMPLE import *

def get_all_test():
    test_list = []
    for name, obj in globals().items():
        if isinstance(obj, type) and issubclass(obj, TestModule) and obj != TestModule:
            instance = obj()
            test_list.append(instance)
    return test_list

if __name__ == "__main__":
    print(get_all_test())