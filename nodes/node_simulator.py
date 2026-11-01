
import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from config import (
    NODES,
    COLLECT_INTERVAL,
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_TOPIC,
    MQTT_KEEPALIVE,
)

# 每个节点独立维护消息序号
sequence_numbers = {
    node["node_id"]: 0 for node in NODES
}


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT服务器连接成功")
    else:
        print(f"MQTT连接失败，错误代码：{reason_code}")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print("MQTT连接断开，等待自动重连...")


def create_sensor_data(node):
    node_id = node["node_id"]
    sequence_numbers[node_id] += 1

    return {
        "node_id": node_id,
        "node_name": node["node_name"],
        "seq": sequence_numbers[node_id],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": round(random.uniform(20, 30), 2),
        "humidity": round(random.uniform(40, 70), 2),
        "light": round(random.uniform(100, 1000), 2),
    }


def main():
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="AIOT_Simulator",
        protocol=mqtt.MQTTv311,
    )

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    print(f"正在连接 MQTT 服务器：{MQTT_BROKER}:{MQTT_PORT}")

    client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        MQTT_KEEPALIVE
    )

    client.loop_start()

    try:
        while True:
            for node in NODES:
                data = create_sensor_data(node)
                payload = json.dumps(data, ensure_ascii=False)

                result = client.publish(
                    MQTT_TOPIC,
                    payload,
                    qos=1
                )

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"发送数据：{payload}")
                else:
                    print(f"发送失败：{node['node_id']}")

            time.sleep(COLLECT_INTERVAL)

    except KeyboardInterrupt:
        print("\n模拟节点停止运行")

    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()

