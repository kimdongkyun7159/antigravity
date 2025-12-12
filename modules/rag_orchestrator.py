"""
RAG Orchestrator - 7개 엔진 통합 및 RAG 파이프라인 관리
"""

from typing import Dict, List, Any, Optional
import hashlib
from datetime import datetime

# 기존 엔진들
from .code_validator import CodeValidator
from .code_executor import CodeExecutor
from .error_analyzer import ErrorAnalyzer
from .error_database import ErrorDatabase
from .pattern_learner import PatternLearner

# RAG 모듈들
from .vector_database import VectorDatabase
from .llm_integration import LLMIntegration
from .config import Config


class RAGOrchestrator:
    """RAG 기반 종합 에러 분석 오케스트레이터"""
    
    def __init__(self, 
                 use_rag: bool = True,
                 gemini_api_key: Optional[str] = None):
        """
        Args:
            use_rag: RAG 기능 사용 여부
            gemini_api_key: Gemini API 키
        """
        print("=" * 60)
        print("🚀 RAG Orchestrator 초기화 중...")
        print("=" * 60)
        
        self.use_rag = use_rag and Config.is_rag_available()
        
        # 기존 데이터베이스
        self.error_db = ErrorDatabase()
        
        # RAG 구성요소
        if self.use_rag:
            try:
                self.vector_db = VectorDatabase()
                self.llm = LLMIntegration(api_key=gemini_api_key)
                print("✅ RAG 모드 활성화")
            except Exception as e:
                print(f"⚠️ RAG 초기화 실패: {e}")
                print("📋 기본 모드로 전환")
                self.use_rag = False
        
        if not self.use_rag:
            print("📋 기본 분석 모드로 동작")
        
        print("=" * 60)
    
    def analyze_with_rag(self, code: str, file_type: str = 'python') -> Dict[str, Any]:
        """
        RAG 기반 종합 분석
        
        Args:
            code: 분석할 코드
            file_type: 파일 타입
            
        Returns:
            종합 분석 결과
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'use_rag': self.use_rag,
            'analysis': {}
        }
        
        # 1단계: 모든 엔진 실행
        print("\n🔍 1단계: 7개 엔진 실행 중...")
        engine_results = self._run_all_engines(code, file_type)
        result['engine_results'] = engine_results
        
        # 에러가 없으면 종료
        if engine_results.get('executor', {}).get('success', True):
            result['status'] = 'success'
            result['message'] = '✅ 코드가 성공적으로 실행되었습니다'
            return result
        
        # 2단계: 에러 분석
        print("📊 2단계: 에러 분석 중...")
        error_info = self._extract_error_info(engine_results)
        result['error_info'] = error_info
        
        if not error_info:
            result['status'] = 'unknown_error'
            result['message'] = '⚠️ 에러 정보를 추출할 수 없습니다'
            return result
        
        # 3단계: RAG 검색 (활성화된 경우)
        similar_cases = []
        if self.use_rag:
            print("🔎 3단계: Vector DB 검색 중...")
            try:
                similar_cases = self.vector_db.search_similar(
                    error_info,
                    top_k=Config.TOP_K_SIMILAR_ERRORS
                )
                result['similar_cases'] = similar_cases
                print(f"   → {len(similar_cases)}개의 유사 사례 발견")
            except Exception as e:
                print(f"   ⚠️ Vector 검색 실패: {e}")
        
        # 4단계: 컨텍스트 구성
        print("📝 4단계: 컨텍스트 구성 중...")
        context = self._build_context(engine_results, error_info, similar_cases)
        
        # 5단계: LLM 해결책 생성 (RAG 모드)
        if self.use_rag and self.llm.available:
            print("🤖 5단계: AI 해결책 생성 중...")
            try:
                ai_solution = self.llm.generate_solution(context)
                result['ai_solution'] = ai_solution
                print("   ✅ AI 해결책 생성 완료")
            except Exception as e:
                print(f"   ⚠️ AI 생성 실패: {e}")
                result['ai_solution'] = self._get_basic_solution(engine_results)
        else:
            # Fallback: 기본 해결책
            result['ai_solution'] = self._get_basic_solution(engine_results)
        
        # 6단계: 결과 저장
        print("💾 6단계: 결과 저장 중...")
        self._save_results(code, error_info, result.get('ai_solution', ''))
        
        result['status'] = 'analyzed'
        print("✅ 분석 완료!")
        
        return result
    
    def _run_all_engines(self, code: str, file_type: str) -> Dict[str, Any]:
        """모든 엔진 실행"""
        results = {}
        
        # Engine 1: Code Validator (정적 분석)
        if file_type == 'python':
            try:
                results['validator'] = CodeValidator.full_validation(code)
            except Exception as e:
                results['validator'] = {'error': str(e)}
        
        # Engine 2: Code Executor (실행)
        try:
            results['executor'] = CodeExecutor.safe_execute(code)
        except Exception as e:
            results['executor'] = {'success': False, 'error': str(e)}
        
        # Engine 3: Error Analyzer (에러 분석)
        if not results['executor'].get('success', False):
            stderr = results['executor'].get('stderr', '')
            if stderr:
                try:
                    results['analyzer'] = ErrorAnalyzer.analyze_error(stderr, code)
                except Exception as e:
                    results['analyzer'] = {'error': str(e)}
        
        # Engine 4: Pattern Learner (통계)
        try:
            results['patterns'] = PatternLearner.get_error_statistics(self.error_db, limit=5)
        except Exception as e:
            results['patterns'] = {'error': str(e)}
        
        return results
    
    def _extract_error_info(self, engine_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """엔진 결과에서 에러 정보 추출"""
        analyzer = engine_results.get('analyzer', {})
        
        if not analyzer or 'error_type' not in analyzer:
            return None
        
        return {
            'error_type': analyzer.get('error_type', 'Unknown'),
            'error_message': analyzer.get('error_message', ''),
            'line_number': analyzer.get('line_number', 0),
            'description': analyzer.get('description', ''),
            'code_snippet': analyzer.get('code_snippet', ''),
            'severity': analyzer.get('severity', 'medium')
        }
    
    def _build_context(self, 
                      engine_results: Dict[str, Any],
                      error_info: Dict[str, Any],
                      similar_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """RAG 컨텍스트 구성"""
        return {
            'current_error': error_info,
            'validator_result': engine_results.get('validator', {}),
            'executor_result': engine_results.get('executor', {}),
            'analyzer_result': engine_results.get('analyzer', {}),
            'pattern_result': engine_results.get('patterns', {}),
            'similar_cases': similar_cases
        }
    
    def _get_basic_solution(self, engine_results: Dict[str, Any]) -> str:
        """기본 해결책 (LLM 없이)"""
        analyzer = engine_results.get('analyzer', {})
        
        solution = f"""### 🔍 문제 진단
{analyzer.get('description', '에러가 발생했습니다')}

### 💡 해결 방법
"""
        
        solutions = analyzer.get('solutions', [])
        for i, sol in enumerate(solutions, 1):
            solution += f"{i}. {sol}\n"
        
        return solution
    
    def _save_results(self, code: str, error_info: Dict[str, Any], solution: str):
        """결과 저장 (SQLite + Vector DB)"""
        try:
            # SQLite 저장
            error_id = self.error_db.save_error(code, error_info)
            
            # Vector DB 저장 (RAG 모드)
            if self.use_rag:
                error_id_str = f"error_{error_id}_{hashlib.md5(code.encode()).hexdigest()[:8]}"
                self.vector_db.add_error(
                    error_id_str,
                    error_info,
                    solution
                )
        except Exception as e:
            print(f"   ⚠️ 저장 실패: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보"""
        stats = {
            'rag_enabled': self.use_rag,
            'sqlite': self.error_db.get_statistics()
        }
        
        if self.use_rag:
            stats['vector_db'] = self.vector_db.get_statistics()
        
        return stats


# 테스트
if __name__ == '__main__':
    print("=" * 60)
    print("🧪 RAG Orchestrator 종합 테스트")
    print("=" * 60)
    
    # RAG Orchestrator 초기화
    orchestrator = RAGOrchestrator(use_rag=True)
    
    # 테스트 코드 1: ModuleNotFoundError
    test_code = """
import numpy as np
print(np.array([1, 2, 3]))
"""
    
    print("\n" + "=" * 60)
    print("📝 테스트: ModuleNotFoundError")
    print("=" * 60)
    
    result = orchestrator.analyze_with_rag(test_code)
    
    print("\n" + "=" * 60)
    print("📊 분석 결과")
    print("=" * 60)
    print(f"상태: {result['status']}")
    print(f"RAG 사용: {result['use_rag']}")
    
    if 'ai_solution' in result:
        print("\n🤖 AI 해결책:")
        print(result['ai_solution'])
    
    # 통계
    print("\n" + "=" * 60)
    print("📈 통계")
    print("=" * 60)
    stats = orchestrator.get_statistics()
    print(f"RAG 활성화: {stats['rag_enabled']}")
    print(f"SQLite 에러 수: {stats['sqlite']['total_errors']}")
    if 'vector_db' in stats:
        print(f"Vector DB 임베딩 수: {stats['vector_db']['total_embeddings']}")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)
