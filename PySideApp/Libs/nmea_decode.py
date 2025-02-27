from datetime import datetime, timezone

import numpy as np

def parse_and_convert_GP(txt_file_path: str = None):
    """
    数据解析
    :param txt_file_path:
    :return xyz_coordinates: list
    :return speed_list:
    """

    def utc_to_timestamp(utc_str):
        """
        将GPGGA的UTC时间字符串转换为UNIX时间戳
        UTC时间格式为HHMMSS.SS
        """
        try:
            # 获取当前日期
            current_date = datetime.now().strftime("%Y-%m-%d")

            # 解析UTC时间字符串
            hours = int(utc_str[0:2])
            minutes = int(utc_str[2:4])
            seconds = float(utc_str[4:])

            # 组合完整的时间字符串
            time_str = f"{current_date} {hours:02d}:{minutes:02d}:{seconds:06.3f}"

            # 转换为datetime对象
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")

            # 设置时区为UTC
            dt = dt.replace(tzinfo=timezone.utc)

            # 转换为UNIX时间戳
            timestamp = dt.timestamp()

            return timestamp
        except Exception as e:
            print(f"Time conversion error: {e}")
            return None

    def gpgga_core(string,):
        """
        仅支持gpgga
        """
        gpgga_dict = None
        if string.startswith('$GPGGA'):
            gpgga_dict = split_GPGGA(string.strip())
            if gpgga_dict is None:
                return None
            else:
                gpgga_data.append(gpgga_dict)
        else:
            return None


    gpgga_data = []
    utc_times, timestamps, lats, lons, heights = [], [], [], [], []
    speed_list = []
    if txt_file_path is not None:
        with open(txt_file_path, 'r', encoding="UTF-8") as file:
            for line in file:
                if line.startswith('b'):
                    cleaned_string = line[2:-1]
                    normal_string = cleaned_string.encode('utf-8').decode('unicode_escape')
                    normal_string = normal_string.splitlines()
                    for _ in normal_string:
                        gpgga_core(_,)
                else:
                    gpgga_core(line, )

    for gp_dict in gpgga_data:
        utc_time = float(gp_dict["utc"])
        timestamp = utc_to_timestamp(gp_dict["utc"])
        if timestamp is not None:
            utc_times.append(utc_time)
            timestamps.append(float(timestamp))
            lats.append(float(gp_dict["纬度"]))
            lons.append(float(gp_dict["经度"]))
            heights.append(float(gp_dict["海拔"]))

    if len(lats) == 0:
        return None

    # # 转换为 NumPy 数组
    # utc_times = np.array(utc_times)
    # timestamps = np.array(timestamps)
    # lats = np.array(lats)
    # lons = np.array(lons)
    # heights = np.array(height)

    # 将所有数据组合成一个数组
    result = [lats, lons, heights, timestamps, ]

    return result

def split_GPGGA(GPGGA_str: str):
    split_list = GPGGA_str.split(sep=",", )
    if not '*' in (split_list[-1]):
        print(f'Not Complete!\n{GPGGA_str}')
        return None
    try:
        GPGGA_dict = {
            "utc": split_list[1],
            "纬度": split_list[2],
            "纬度指示": split_list[3],
            "经度": split_list[4],
            "经度指示": split_list[5],
            "GPS状态": split_list[6],
            "参与解算的卫星数量": split_list[7],
            "HDOP水平精度因子": split_list[8],
            "海拔": split_list[9],
            "海拔单位": split_list[10],
            "大地水准": split_list[11],
            "水准单位": split_list[12],
            "差分时间": split_list[13],
            "差分站ID&校验": split_list[14],

        }
    except Exception as e:
        print(GPGGA_str)
        print(f"{e}")
        return None
    if GPGGA_dict['GPS状态'] != '4':
        print('非基站解')
        return None
    return GPGGA_dict

if __name__ == "__main__":
    file_path = '../data_source/output.txt'
    array_result = parse_and_convert_GP(file_path)
    pass
