import json
import os
import sys
import time
import requests
import logging
from abc import ABC, abstractmethod

# 配置 logging，强制输出到 stdout
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
    
    def log(self, msg):
        logger.info(f"[{self.worker_name}] {msg}")
    
    def send_message(self, room_id, content, msg_type="m.text"):
        url = f"{self.matrix_homeserver}/_matrix/client/v3/rooms/{room_id}/send/m.room.message"
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        data = {"msgtype": msg_type, "body": content}
        
        for attempt in range(5):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=10)
                if response.status_code == 200:
                    self.log(f"Message sent to {room_id}")
                    return response.json()
                self.log(f"Send failed (attempt {attempt+1}): {response.status_code}")
            except Exception as e:
                self.log(f"Send exception (attempt {attempt+1}): {e}")
            time.sleep(2 ** attempt)
        return None
    
    def send_task_complete(self, task_id, result):
        message = {"type": "task_complete", "worker": self.worker_name, "task_id": task_id, "result": result}
        self.send_message(self.manager_room, json.dumps(message))
    
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
        for attempt in range(10):
            try:
                self.announce_startup()
                self.log("Matrix connection successful")
                break
            except Exception as e:
                self.log(f"Waiting for Matrix: {e}")
                time.sleep(3)
        
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