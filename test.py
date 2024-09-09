
import socket
import time

def test_udp_port(ip, port):
    # 创建一个 UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)  # 设置超时时间为 1 秒

    try:
        # 发送测试数据
        message = b'Test'
        sock.sendto(message, (ip, port))

        # 等待响应
        start_time = time.time()
        while True:
            try:
                data, server = sock.recvfrom(4096)  # 接收响应
                print(f"UDP port {port} on {ip} is open. Response: {data}")
                break
            except socket.timeout:
                # 如果超时，检查是否超过 2 秒
                if time.time() - start_time > 2:
                    print(f"UDP port {port} on {ip} is closed or not responding.")
                    break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    test_ip = input("183.134.186.124")
    test_port = int(input(10995))
    test_udp_port(test_ip, test_port)