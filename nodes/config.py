# 模拟节点配置

NODES = [
    {
        "node_id": "Node001",
        "node_name": "环境监测节点1"
    },
    {
        "node_id": "Node002",
        "node_name": "环境监测节点2"
    }
]

# 数据采集间隔（秒）
COLLECT_INTERVAL = 2

# MQTT配置
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "aiot/environment"
MQTT_KEEPALIVE = 60
