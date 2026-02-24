import sys
from unittest.mock import MagicMock, AsyncMock

# Mock heavy dependencies before tests run
sys.modules['torch'] = MagicMock()
sys.modules['transformers'] = MagicMock()
sys.modules['whisper'] = MagicMock()
sys.modules['TTS'] = MagicMock()
sys.modules['TTS.api'] = MagicMock()
sys.modules['chromadb'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['redis'] = MagicMock()
sys.modules['prometheus_client'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['langdetect'] = MagicMock()

# Mock settings to avoid loading .env
import os
os.environ["APP_NAME"] = "KIONI"
os.environ["HUGGINGFACE_TOKEN"] = "test"

# Create a more realistic settings mock
class MockSettings:
    def __init__(self):
        self.APP_NAME = 'KIONI'
        self.VERSION = '1.0.0'
        self.CHROMA_PERSIST_DIR = './chroma_db'
        self.COLLECTION_NAME = 'test'
        self.VISION_MODEL = 'test'
        self.WHISPER_MODEL = 'test'
        self.TTS_MODEL = 'test'
        self.TEXT_MODEL_PRIMARY = 'test'
        self.TEXT_MODEL_FALLBACK = 'test'
        self.HUGGINGFACE_TOKEN = 'test'
        self.SWAHILI_ROBERTA = 'test'
        self.SHENG_DETECTION = True
        self.WS_HEARTBEAT_INTERVAL = 30
        self.MAX_AUDIO_SIZE = 10 * 1024 * 1024
        self.SUPPORTED_AUDIO_FORMATS = ["wav", "mp3", "webm", "ogg"]
        self.CAMERA_FRAME_INTERVAL = 5.0
        self.VISION_CONFIDENCE_THRESHOLD = 0.6
        self.DEFAULT_PERSONALITY = {
                "urafiki": 80,
                "ucheshi": 60,
                "hekima": 70,
                "msaada": 90,
                "mode": "rafiki"
            }

settings_mock = MockSettings()
sys.modules['app.config'] = MagicMock()
from app.config import settings
for attr in dir(settings_mock):
    if not attr.startswith('__'):
        setattr(settings, attr, getattr(settings_mock, attr))

# Mock database
db_manager_mock = MagicMock()
db_manager_mock.store_conversation = AsyncMock()
db_manager_mock.get_conversation_history = AsyncMock(return_value=[])
db_manager_mock.search_similar = AsyncMock(return_value={'documents': [], 'ids': []})
db_manager_mock.delete_session = AsyncMock()

db_module_mock = MagicMock()
db_module_mock.db_manager = db_manager_mock
sys.modules['app.models.database'] = db_module_mock
