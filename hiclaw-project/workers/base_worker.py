import json
import os
import sys
import time
import requests
import logging
import uuid
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger('worker')


class BaseWorker(ABC):
    def __init__(self):
        self.worker_name = os.environ.get('HICLAW_WORKER_NAME', 'unknown')
        self.matrix_homeserver = os.environ.get('MATRIX_HOMESERVER', 'http://synapse:8008')
        self.manager_room = os.environ.get('MANAGER_ROOM', '!manager:localhost')
        self.access_token = os.environ.get('MATRIX_ACCESS_TOKEN', '')
        self.running = True
        self.check_interval = 5

        # ✅ 新增：防止重复发送
        self._sent_cache = set()

    def log(self, msg):
        logger.info(f"[{self.worker_name}] {msg}")

    # ==============================
    # ✅ 核心修复：稳定发送消息
    # ==============================
    def send_message(self, room_id, content, msg_type="m.text"):

        # ✅ 防重复发送（关键修复）
        cache_key = f"{room_id}:{content}"
        if cache_key in self._sent_cache:
            return {"skipped": True}

        self._sent_cache.add(cache_key)

        url = f"{self.matrix_homeserver}/_matrix/client/v3/rooms/{room_id}/send/m.room.message"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "msgtype": msg_type,
            "body": content,
            # ✅ Matrix 推荐：transaction_id 防重复
            "txn_id": str(uuid.uuid4())
        }

        last_response = None

        for attempt in range(3):  # ❗降低 retry，避免刷 403 噪音
            try:
                response = requests.post(url, headers=headers, json=data, timeout=10)
                last_response = response

                if response.status_code in [200, 201]:
                    self.log(f"Message sent to {room_id}")
                    return response.json()

                # ❗403 不再疯狂 retry（关键修复）
                if response.status_code == 403:
                    self.log(f"Send blocked (403) - stop retrying")
                    break

                self.log(f"Send failed (attempt {attempt+1}): {response.status_code}")

            except Exception as e:
                self.log(f"Send exception (attempt {attempt+1}): {e}")

            time.sleep(1)

        return None

    # ==============================
    def send_task_complete(self, task_id, result):
        message = {
            "type": "task_complete",
            "worker": self.worker_name,
            "worker_type": "developer", 
            "task_id": task_id,
            "result": result
        }

    # 👉 只打印日志，不发到房间
        self.log(f"Task complete: {task_id}")
        self.log(f"Result ready for manager system")
    
    # 👉 如果你未来有 Manager API，可以在这里 HTTP POST
        return message
    # ==============================
    def announce_startup(self):
        self.log("Worker starting...")
        self.send_message(self.manager_room, f"Worker {self.worker_name} ready")

    def get_pending_task(self):
        task_json = os.environ.get('PENDING_TASK', '')
        if task_json:
            os.environ['PENDING_TASK'] = ''
            return json.loads(task_json)
        return None

    @abstractmethod
    def run(self, task):
        pass

    def listen(self):
        self.log("=== LISTEN LOOP STARTED ===")

        for _ in range(5):
            try:
                self.announce_startup()
                self.log("Matrix connection successful")
                break
            except Exception as e:
                self.log(f"Waiting for Matrix: {e}")
                time.sleep(2)

        while self.running:
            try:
                task = self.get_pending_task()
                if task:
                    self.log(f"Received task: {task.get('task_id')}")
                    self.run(task)
                else:
                    time.sleep(self.check_interval)

            except Exception as e:
                self.log(f"Error: {e}")
                time.sleep(5)