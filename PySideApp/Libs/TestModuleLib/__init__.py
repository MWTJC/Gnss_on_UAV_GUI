from PySideApp.Libs.TestModuleLib.GBT2038058_2019 import *
from PySideApp.Libs.TestModuleLib.Tools import *

def get_all_test():
    test_list = []
    for name, obj in globals().items():
        if isinstance(obj, type) and issubclass(obj, TestModule) and obj != TestModule:
            instance = obj()
            test_list.append(instance)
    return test_list

if __name__ == "__main__":
    print(get_all_test())