import aioserial
import asyncio


async def send_hex_data():
    # 打开发送端串口
    ser_send = aioserial.AioSerial(port='COM1', baudrate=115200,
                                               bytesize=8, parity="N",
                                               stopbits=1)

    # 读取本地hex文件
    with open('../proj_file/20250426-1.hex', 'rb') as f:
        hex_data = f.read()

    chunk_size = 158  # 每次发送的字节数

    while True:
        # 将数据按158字节分割
        for i in range(0, len(hex_data), chunk_size):
            chunk = hex_data[i:i + chunk_size]
            await ser_send.write_async(chunk)
            print(f"Sent chunk {i // chunk_size + 1}: {chunk.hex()}")
            await asyncio.sleep(1)  # 每个数据包之间添加小延时

        print("Complete one round of sending, starting next round...")
        await asyncio.sleep(1)  # 完成一轮发送后等待1秒


async def receive_data():
    # 打开接收端串口
    ser_receive = aioserial.AioSerial(port='COM2', baudrate=115200,
                                               bytesize=8, parity="N",
                                               stopbits=1)

    while True:
        data = await ser_receive.read_async()
        print(f"Received: {data.hex()}")


# 运行发送和接收任务
async def main():
    await asyncio.gather(
        send_hex_data(),
        # receive_data()
    )


if __name__ == "__main__":
    asyncio.run(main())
