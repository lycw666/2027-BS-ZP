
import json
import sqlite3
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

# MQTT配置
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "aiot/environment"

# 数据库文件
DB_PATH = "environment.db"


def init_database():
    """初始化SQLite数据库"""
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT NOT NULL,
            node_name TEXT,
            seq INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL,
            humidity REAL,
            light REAL,
            received_at TEXT NOT NULL,
            UNIQUE(node_id, seq)
        )
    """)

    conn.commit()
    conn.close()

    print("SQLite数据库初始化成功")


def save_data(data):
    """保存传感器数据"""
    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("""
            INSERT OR IGNORE INTO sensor_data (
                node_id,
                node_name,
                seq,
                timestamp,
                temperature,
                humidity,
                light,
                received_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["node_id"],
            data.get("node_name"),
            data["seq"],
            data["timestamp"],
            data.get("temperature"),
            data.get("humidity"),
            data.get("light"),
            datetime.now(timezone.utc).isoformat()
        ))

        conn.commit()

        if conn.total_changes > 0:
            print(
                f"数据入库成功：{data['node_id']} "
                f"序号={data['seq']}"
            )
        else:
            print(
                f"重复数据，已忽略：{data['node_id']} "
                f"序号={data['seq']}"
            )

    except (KeyError, ValueError, TypeError) as error:
        print(f"数据格式错误：{error}")

    finally:
        conn.close()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT服务器连接成功")
        client.subscribe(MQTT_TOPIC, qos=1)
        print(f"已订阅主题：{MQTT_TOPIC}")
    else:
        print(f"MQTT连接失败：{reason_code}")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        save_data(data)

    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        print(f"消息解析失败：{error}")


def main():
    init_database()

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="AIOT_Data_Receiver",
        protocol=mqtt.MQTTv311
    )

    client.on_connect = on_connect
    client.on_message = on_message

    print("正在启动数据接收服务...")

    client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        60
    )

    try:
        client.loop_forever()

    except KeyboardInterrupt:
        print("数据接收服务已停止")
        client.disconnect()


if __name__ == "__main__":
    main()

