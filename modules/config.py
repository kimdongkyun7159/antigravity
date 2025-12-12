"""
설정 모듈 - RAG 및 시스템 설정 관리
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Config:
    """시스템 설정"""
    
    # ========== API 키 ==========
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # ========== Vector DB 설정 ==========
    VECTOR_DB_PATH = './data/chroma'
    VECTOR_COLLECTION_NAME = 'error_history'
    EMBEDDING_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'  # 한글 지원
    
    # ========== RAG 설정 ==========
    RAG_ENABLED = os.getenv('RAG_ENABLED', 'true').lower() == 'true'
    TOP_K_SIMILAR_ERRORS = int(os.getenv('TOP_K_SIMILAR_ERRORS', '5'))
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))  # 70% 이상 유사도
    
    # ========== LLM 설정 ==========
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')  # 'gemini' or 'ollama'
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-pro')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.3'))  # 낮을수록 일관성↑
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '1000'))
    
    # Ollama 설정 (로컬 LLM 대안)
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
    
    # ========== 데이터베이스 설정 ==========
    SQLITE_DB_PATH = './data/error_history.db'
    
    # ========== 캐싱 설정 ==========
    ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1시간
    
    # ========== 성능 설정 ==========
    MAX_CODE_LENGTH = 10 * 1024 * 1024  # 10MB
    EXECUTION_TIMEOUT = 30  # 초
    
    # ========== 디렉토리 ==========
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    UPLOAD_DIR = BASE_DIR / 'uploads'
    
    @classmethod
    def ensure_directories(cls):
        """필요한 디렉토리 생성"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        Path(cls.VECTOR_DB_PATH).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def is_rag_available(cls) -> bool:
        """RAG 기능 사용 가능 여부"""
        if not cls.RAG_ENABLED:
            return False
        
        # Gemini API 키 확인
        if cls.LLM_PROVIDER == 'gemini' and not cls.GEMINI_API_KEY:
            return False
        
        return True
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """설정 요약"""
        return {
            'rag_enabled': cls.RAG_ENABLED,
            'rag_available': cls.is_rag_available(),
            'llm_provider': cls.LLM_PROVIDER,
            'embedding_model': cls.EMBEDDING_MODEL,
            'top_k': cls.TOP_K_SIMILAR_ERRORS,
            'vector_db_path': cls.VECTOR_DB_PATH
        }


# 초기화 시 디렉토리 생성
Config.ensure_directories()


if __name__ == '__main__':
    print("=" * 60)
    print("⚙️  설정 정보")
    print("=" * 60)
    
    summary = Config.get_config_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
