import struct
import binascii

from loguru import logger


class PVAPacket:
    def __init__(self):
        # 帧头
        self.header_protocol = None  # 协议 (AC)
        self.header_seq = None  # 字节序号 (0)

        # 数据体
        self.byte1 = None  # 1 (55)
        self.byte2 = None  # 2 (96)
        self.byte3 = None  # 3 (83)
        self.protocol_type = None  # 4-5 协议类型
        self.reserved1 = None  # 6-7 保留位
        self.data_length = None  # 8-11 数据长度
        self.info_id = None  # 12-13 信息ID
        self.payload_length = None  # 14-15 数据内容长度
        self.time_status = None  # 16-17 时间状态
        self.gps_week = None  # 18-19 GPS周
        self.gps_week_seconds = None  # 20-23 GPS周内秒
        self.reserved2 = None  # 24-27 保留位
        self.combined_status = None  # 28-31 组合状态
        self.position_type = None  # 32-35 定位类型
        self.latitude = None  # 36-43 纬度
        self.longitude = None  # 44-51 经度
        self.altitude = None  # 52-59 海拔高
        self.altitude_std = None  # 60-63 高程异常值
        self.north_velocity = None  # 64-71 北向速度
        self.east_velocity = None  # 72-79 东向速度
        self.up_velocity = None  # 80-87 天向速度
        self.roll = None  # 88-95 横滚
        self.pitch = None  # 96-103 俯仰
        self.heading = None  # 104-111 航向
        self.lat_std = None  # 112-115 纬度自评估偏差
        self.lon_std = None  # 116-119 经度自评估偏差
        self.alt_std = None  # 120-123 海拔自评估偏差
        self.north_vel_std = None  # 124-127 北向速度自评估偏差
        self.east_vel_std = None  # 128-131 东向速度自评估偏差
        self.up_vel_std = None  # 132-135 天向速度自评估偏差
        self.roll_std = None  # 136-139 横滚自评估偏差
        self.pitch_std = None  # 140-143 俯仰自评估偏差
        self.heading_std = None  # 144-147 航向自评估偏差
        self.ext_status = None  # 148-151 扩展状态字
        self.pos_update_time = None  # 152-153 自位置更新以来的时间

        # 校验
        self.crc = None  # 154-157 32位CRC校验

    def __str__(self):
        """返回报文的可读字符串表示"""
        return (
            f"PVA数据报文:\n"
            f"帧头: 协议={self.header_protocol}, 序号={self.header_seq}\n"
            f"数据: 字节1-3={self.byte1},{self.byte2},{self.byte3}\n"
            f"协议类型: {self.protocol_type}\n"
            f"数据长度: {self.data_length}\n"
            f"信息ID: {self.info_id}\n"
            f"位置信息: 纬度={self.latitude}°, 经度={self.longitude}°, 海拔={self.altitude}米\n"
            f"速度信息: 北向={self.north_velocity}m/s, 东向={self.east_velocity}m/s, 天向={self.up_velocity}m/s\n"
            f"姿态信息: 横滚={self.roll}°, 俯仰={self.pitch}°, 航向={self.heading}°\n"
            f"CRC校验: {hex(self.crc) if self.crc is not None else None}\n"
        )


def find_packet_start(data, start_pos=0):
    """
    在数据中查找报文开始的位置
    寻找特征序列: AC 55 96 83
    """
    pattern = b'\xAC\x55\x96\x83'
    pos = data.find(pattern, start_pos)
    return pos


def parse_packet(data, offset=0):
    """解析单个PVA报文"""
    if len(data) - offset < 158:  # 确保数据长度足够
        return None, offset

    packet = PVAPacket()

    # 解析帧头
    packet.header_protocol = data[offset]  # AC
    packet.byte1 = data[offset + 1]  # 55
    packet.byte2 = data[offset + 2]  # 96
    packet.byte3 = data[offset + 3]  # 83

    # 使用struct模块解析二进制数据
    packet.protocol_type = struct.unpack('<H', data[offset + 4:offset + 6])[0]
    packet.reserved1 = struct.unpack('<H', data[offset + 6:offset + 8])[0]
    packet.data_length = struct.unpack('<L', data[offset + 8:offset + 12])[0]
    packet.info_id = struct.unpack('<H', data[offset + 12:offset + 14])[0]
    packet.payload_length = struct.unpack('<H', data[offset + 14:offset + 16])[0]
    packet.time_status = struct.unpack('<H', data[offset + 16:offset + 18])[0]
    packet.gps_week = struct.unpack('<H', data[offset + 18:offset + 20])[0]
    packet.gps_week_seconds = struct.unpack('<L', data[offset + 20:offset + 24])[0]
    packet.reserved2 = struct.unpack('<L', data[offset + 24:offset + 28])[0]
    packet.combined_status = struct.unpack('<L', data[offset + 28:offset + 32])[0]
    packet.position_type = struct.unpack('<L', data[offset + 32:offset + 36])[0]

    # 解析双精度浮点数和单精度浮点数
    packet.latitude = struct.unpack('<d', data[offset + 36:offset + 44])[0]
    packet.longitude = struct.unpack('<d', data[offset + 44:offset + 52])[0]
    packet.altitude = struct.unpack('<d', data[offset + 52:offset + 60])[0]
    packet.altitude_std = struct.unpack('<f', data[offset + 60:offset + 64])[0]
    packet.north_velocity = struct.unpack('<d', data[offset + 64:offset + 72])[0]
    packet.east_velocity = struct.unpack('<d', data[offset + 72:offset + 80])[0]
    packet.up_velocity = struct.unpack('<d', data[offset + 80:offset + 88])[0]
    packet.roll = struct.unpack('<d', data[offset + 88:offset + 96])[0]
    packet.pitch = struct.unpack('<d', data[offset + 96:offset + 104])[0]
    packet.heading = struct.unpack('<d', data[offset + 104:offset + 112])[0]

    packet.lat_std = struct.unpack('<f', data[offset + 112:offset + 116])[0]
    packet.lon_std = struct.unpack('<f', data[offset + 116:offset + 120])[0]
    packet.alt_std = struct.unpack('<f', data[offset + 120:offset + 124])[0]
    packet.north_vel_std = struct.unpack('<f', data[offset + 124:offset + 128])[0]
    packet.east_vel_std = struct.unpack('<f', data[offset + 128:offset + 132])[0]
    packet.up_vel_std = struct.unpack('<f', data[offset + 132:offset + 136])[0]
    packet.roll_std = struct.unpack('<f', data[offset + 136:offset + 140])[0]
    packet.pitch_std = struct.unpack('<f', data[offset + 140:offset + 144])[0]
    packet.heading_std = struct.unpack('<f', data[offset + 144:offset + 148])[0]

    packet.ext_status = struct.unpack('<L', data[offset + 148:offset + 152])[0]
    packet.pos_update_time = struct.unpack('<H', data[offset + 152:offset + 154])[0]

    # 解析CRC校验
    packet.crc = struct.unpack('<L', data[offset + 154:offset + 158])[0]
    return packet, offset + 158  # 返回解析的报文、新的偏移量和校验结果


def parse_pva_file(file_path, max_packets=None):
    """
    解析包含多个PVA报文的文件

    参数:
        file_path: 文件路径
        max_packets: 最大解析报文数量，None表示解析所有报文

    返回:
        解析的报文列表
    """
    packets = []

    try:
        with open(file_path, 'rb') as f:
            data = f.read()

        offset = 0
        packet_count = 0

        while offset < len(data):
            # 查找报文开始位置
            start_pos = find_packet_start(data, offset)
            if start_pos == -1:
                break

            offset = start_pos
            packet, new_offset, is_valid = parse_packet(data, offset)

            if packet:
                packets.append((packet, is_valid))
                offset = new_offset
                packet_count += 1

                if max_packets and packet_count >= max_packets:
                    break
            else:
                # 如果解析失败，尝试下一个位置
                offset += 1

    except Exception as e:
        logger.error(f"解析文件时出错: {e}")

    return packets


def main():
    # 使用示例
    file_path = "pva/d0000006.txt"


    logger.info(f"开始解析文件 {file_path}...")
    packets = parse_pva_file(file_path)

    logger.success(f"成功解析 {len(packets)} 个报文")

    # 输出解析结果
    for i, (packet, is_valid) in enumerate(packets):
        logger.info(f"\n报文 #{i + 1} {'(校验通过)' if is_valid else '(校验失败)'}")
        logger.info(packet)

    # 统计校验通过的报文数量
    valid_packets = sum(1 for _, is_valid in packets if is_valid)
    logger.info(f"\n校验通过: {valid_packets}/{len(packets)}")


if __name__ == "__main__":
    main()
