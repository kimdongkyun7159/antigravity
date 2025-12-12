"""
Vector Database 모듈 - RAG 기반 에러 검색 (간소화 버전)
ChromaDB 기본 임베딩 사용 (의존성 최소화)
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import Dict, List, Any, Optional
import os
import json
from pathlib import Path


class VectorDatabase:
    """벡터 데이터베이스 - 에러 임베딩 및 유사도 검색 (간소화 버전)"""
    
    def __init__(self, 
                 db_path: str = './data/chroma',
                 collection_name: str = 'error_history'):
        """
        Args:
            db_path: ChromaDB 저장 경로
            collection_name: 컬렉션 이름
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        # 디렉토리 생성
        os.makedirs(db_path, exist_ok=True)
        
        print("📦 Vector Database 초기화 중...")
        
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(path=db_path)
        
        # 기본 임베딩 함수 사용 (SentenceTransformer 대신 ChromaDB 내장)
        # 더 가볍고 빠르게 동작
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        
        # 컬렉션 생성/로드
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=default_ef,
            metadata={"description": "Error analysis history with embeddings"}
        )
        
        print("✅ Vector Database 초기화 완료")
    
    def _build_error_text(self, error_info: Dict[str, Any]) -> str:
        """
        에러 정보를 검색 가능한 텍스트로 변환
        
        Args:
            error_info: 에러 분석 결과
            
        Returns:
            결합된 텍스트
        """
        error_type = error_info.get('error_type', '')
        error_message = error_info.get('error_message', '')
        code_snippet = error_info.get('code_snippet', '')[:200]
        description = error_info.get('description', '')
        
        # 종합 텍스트 생성
        combined_text = f"""
Error Type: {error_type}
Message: {error_message}
Description: {description}
Code: {code_snippet}
""".strip()
        
        return combined_text
    
    def add_error(self, 
                  error_id: str,
                  error_info: Dict[str, Any],
                  solution: str,
                  metadata: Optional[Dict[str, Any]] = None):
        """
        새 에러와 해결책 저장
        
        Args:
            error_id: 고유 ID
            error_info: 에러 분석 결과
            solution: 해결책
            metadata: 추가 메타데이터
        """
        # 메타데이터 준비 (ChromaDB는 간단한 타입만 지원)
        meta = {
            'error_type': str(error_info.get('error_type', 'Unknown')),
            'error_message': str(error_info.get('error_message', ''))[:200],
            'line_number': int(error_info.get('line_number', 0)),
            'severity': str(error_info.get('severity', 'medium')),
            'solution_preview': str(solution)[:200]
        }
        
        # 추가 메타데이터 병합
        if metadata:
            for k, v in metadata.items():
                meta[k] = str(v)  # 문자열로 변환
        
        # 문서 생성 (검색 시 반환될 텍스트)
        document = f"""
{error_info.get('error_type', 'Unknown')}: {error_info.get('error_message', '')}

해결책:
{solution}

코드:
{error_info.get('code_snippet', '')[:200]}
""".strip()
        
        # ChromaDB에 추가 (자동으로 임베딩 생성됨)
        try:
            self.collection.add(
                ids=[error_id],
                documents=[document],
                metadatas=[meta]
            )
            return True
        except Exception as e:
            print(f"❌ 저장 실패: {e}")
            return False
    
    def search_similar(self, 
                       error_info: Dict[str, Any],
                       top_k: int = 5,
                       filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        유사한 에러 검색
        
        Args:
            error_info: 검색할 에러 정보
            top_k: 상위 K개 결과
            filter_metadata: 메타데이터 필터
            
        Returns:
            유사 에러 리스트
        """
        # 쿼리 텍스트 생성
        query_text = self._build_error_text(error_info)
        
        try:
            # 검색 실행
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(top_k, self.collection.count()),
                where=filter_metadata  # 필터 적용 (옵션)
            )
            
            # 결과 포맷팅
            similar_errors = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    similar_errors.append({
                        'id': results['ids'][0][i],
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None,
                        'similarity_score': 1 - (results['distances'][0][i] / 2) if 'distances' in results else None
                    })
            
            return similar_errors
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            return []
    
    def search_by_query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        텍스트 쿼리로 검색
        
        Args:
            query_text: 검색 쿼리 (자연어)
            top_k: 상위 K개 결과
            
        Returns:
            검색 결과
        """
        try:
            # 검색
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(top_k, self.collection.count())
            )
            
            # 포맷팅
            similar_errors = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    similar_errors.append({
                        'id': results['ids'][0][i],
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return similar_errors
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Vector DB 통계
        
        Returns:
            통계 정보
        """
        count = self.collection.count()
        
        return {
            'total_embeddings': count,
            'collection_name': self.collection_name,
            'embedding_model': 'ChromaDB Default (all-MiniLM-L6-v2)',
            'db_path': self.db_path
        }
    
    def clear_collection(self):
        """컬렉션 초기화 (테스트용)"""
        try:
            self.client.delete_collection(name=self.collection_name)
            default_ef = embedding_functions.DefaultEmbeddingFunction()
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=default_ef,
                metadata={"description": "Error analysis history with embeddings"}
            )
            return True
        except Exception as e:
            print(f"❌ 초기화 실패: {e}")
            return False
    
    def delete_by_id(self, error_id: str):
        """ID로 에러 삭제"""
        try:
            self.collection.delete(ids=[error_id])
            return True
        except Exception as e:
            print(f"❌ 삭제 실패: {e}")
            return False


# 테스트
if __name__ == '__main__':
    print("=" * 60)
    print("🔍 Vector Database 테스트 (간소화 버전)")
    print("=" * 60)
    
    # Vector DB 초기화
    vdb = VectorDatabase()
    
    # 기존 데이터 초기화
    print("\n🧹 컬렉션 초기화...")
    vdb.clear_collection()
    
    # 테스트 에러 1
    print("\n📝 테스트 에러 추가 중...")
    error1 = {
        'error_type': 'ModuleNotFoundError',
        'error_message': "No module named 'numpy'",
        'line_number': 1,
        'code_snippet': 'import numpy as np',
        'description': 'numpy 패키지가 설치되지 않음',
        'severity': 'high'
    }
    solution1 = "pip install numpy를 실행하여 패키지를 설치하세요."
    
    # 저장
    success = vdb.add_error('error_001', error1, solution1)
    if success:
        print("✅ 에러 1 저장 완료")
    
    # 테스트 에러 2 (유사한 에러)
    error2 = {
        'error_type': 'ModuleNotFoundError',
        'error_message': "No module named 'pandas'",
        'line_number': 1,
        'code_snippet': 'import pandas as pd',
        'description': 'pandas 패키지가 설치되지 않음',
        'severity': 'high'
    }
    solution2 = "pip install pandas를 실행하세요."
    
    vdb.add_error('error_002', error2, solution2)
    print("✅ 에러 2 저장 완료")
    
    # 테스트 에러 3 (다른 타입)
    error3 = {
        'error_type': 'SyntaxError',
        'error_message': "invalid syntax",
        'line_number': 5,
        'code_snippet': 'if x = 10:',
        'description': '할당 연산자를 잘못 사용',
        'severity': 'high'
    }
    solution3 = "비교 연산자 ==를 사용하세요: if x == 10:"
    
    vdb.add_error('error_003', error3, solution3)
    print("✅ 에러 3 저장 완료")
    
    # 유사 에러 검색
    query_error = {
        'error_type': 'ModuleNotFoundError',
        'error_message': "No module named 'scipy'",
        'code_snippet': 'import scipy',
        'description': 'scipy 패키지 없음'
    }
    
    print("\n🔍 유사 에러 검색 중...")
    similar = vdb.search_similar(query_error, top_k=3)
    
    print(f"\n📊 {len(similar)}개의 유사 에러 발견:")
    for i, result in enumerate(similar, 1):
        score = result.get('similarity_score', 0)
        if score:
            print(f"\n{i}. 유사도: {score:.2%}")
        print(f"   에러 타입: {result['metadata']['error_type']}")
        print(f"   메시지: {result['metadata']['error_message'][:50]}...")
        print(f"   해결책: {result['metadata']['solution_preview'][:50]}...")
    
    # 통계
    stats = vdb.get_statistics()
    print(f"\n📈 통계:")
    print(f"   - 총 임베딩: {stats['total_embeddings']}개")
    print(f"   - 모델: {stats['embedding_model']}")
    print(f"   - 경로: {stats['db_path']}")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)
