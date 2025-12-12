"""
LLM Integration 모듈 - Gemini API 통합
"""

import os
from typing import Dict, List, Any, Optional
import json


class LLMIntegration:
    """LLM 통합 - Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Gemini API 키 (None이면 환경변수에서 로드)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', '')
        self.available = bool(self.api_key)
        
        if self.available:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini API 연결 완료")
            except Exception as e:
                print(f"⚠️ Gemini API 초기화 실패: {e}")
                self.available = False
        else:
            print("⚠️ Gemini API 키가 없습니다. Fallback 모드로 동작합니다.")
    
    def generate_solution(self, context: Dict[str, Any]) -> str:
        """
        컨텍스트를 바탕으로 최적의 해결책 생성
        
        Args:
            context: RAG 컨텍스트 (엔진 결과 + 유사 사례)
            
        Returns:
            생성된 해결책
        """
        if not self.available:
            return self._fallback_solution(context)
        
        try:
            prompt = self._build_prompt(context)
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,  # 일관성↑
                    'max_output_tokens': 1000,
                }
            )
            return response.text
        except Exception as e:
            print(f"⚠️ LLM 생성 실패: {e}")
            return self._fallback_solution(context)
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """RAG 프롬프트 구성"""
        
        # 현재 에러 정보
        current_error = context.get('current_error', {})
        error_type = current_error.get('error_type', 'Unknown')
        error_message = current_error.get('error_message', '')
        code_snippet = current_error.get('code_snippet', '')
        
        # 엔진 결과
        validator = context.get('validator_result', {})
        executor = context.get('executor_result', {})
        analyzer = context.get('analyzer_result', {})
        
        # 유사 사례
        similar_cases = context.get('similar_cases', [])
        
        prompt = f"""당신은 Python 에러 분석 전문가입니다.

## 현재 에러 정보
- 에러 타입: {error_type}
- 에러 메시지: {error_message}
- 코드:
```python
{code_snippet}
```

## 분석 엔진 결과

### Code Validator
{json.dumps(validator, ensure_ascii=False, indent=2) if validator else '분석 없음'}

### Code Executor
- 실행 성공: {executor.get('success', False)}
- 에러 출력: {executor.get('stderr', '')[:200]}

### Error Analyzer
- 에러 타입: {analyzer.get('error_type', 'Unknown')}
- 설명: {analyzer.get('description', '')}
- 기본 해결책: {', '.join(analyzer.get('solutions', [])[:2])}

## 과거 유사 사례 ({len(similar_cases)}개)
"""
        
        for i, case in enumerate(similar_cases[:3], 1):
            meta = case.get('metadata', {})
            prompt += f"""
### 사례 {i}
- 에러 타입: {meta.get('error_type', '')}
- 메시지: {meta.get('error_message', '')[:100]}
- 해결책: {meta.get('solution_preview', '')[:150]}
- 유사도: {case.get('similarity_score', 0):.0%}
"""
        
        prompt += """

## 요청사항
위 모든 정보를 종합하여 **가장 정확하고 실용적인 해결책**을 한글로 제시하세요.

다음 형식으로 답변하세요:

### 🔍 문제 진단
[에러의 근본 원인 설명]

### 💡 해결 방법
1. [첫 번째 단계]
2. [두 번째 단계]
3. [세 번째 단계]

### 📋 추가 참고사항
[주의사항이나 추가 팁]

간결하고 명확하게 작성하세요.
"""
        
        return prompt
    
    def _fallback_solution(self, context: Dict[str, Any]) -> str:
        """LLM 없이 기본 해결책 제공"""
        
        current_error = context.get('current_error', {})
        analyzer = context.get('analyzer_result', {})
        similar_cases = context.get('similar_cases', [])
        
        solution = f"""### 🔍 문제 진단
{analyzer.get('description', '에러가 발생했습니다')}

### 💡 해결 방법
"""
        
        # Error Analyzer의 해결책
        solutions = analyzer.get('solutions', [])
        for i, sol in enumerate(solutions, 1):
            solution += f"{i}. {sol}\n"
        
        # 유사 사례가 있으면 추가
        if similar_cases:
            solution += "\n### 📋 유사 사례 참고\n"
            for i, case in enumerate(similar_cases[:2], 1):
                meta = case.get('metadata', {})
                solution += f"{i}. {meta.get('solution_preview', '')[:100]}\n"
        
        return solution


# 테스트
if __name__ == '__main__':
    print("=" * 60)
    print("🤖 LLM Integration 테스트")
    print("=" * 60)
    
    llm = LLMIntegration()
    
    # 테스트 컨텍스트
    test_context = {
        'current_error': {
            'error_type': 'ModuleNotFoundError',
            'error_message': "No module named 'numpy'",
            'code_snippet': 'import numpy as np\nprint(np.array([1,2,3]))'
        },
        'validator_result': {
            'syntax': {'valid': True},
            'imports': {
                'missing': ['numpy']
            }
        },
        'executor_result': {
            'success': False,
            'stderr': "ModuleNotFoundError: No module named 'numpy'"
        },
        'analyzer_result': {
            'error_type': 'ModuleNotFoundError',
            'description': 'numpy 패키지가 설치되지 않았습니다',
            'solutions': [
                'pip install numpy를 실행하세요',
                '가상환경이 활성화되었는지 확인하세요'
            ]
        },
        'similar_cases': [
            {
                'metadata': {
                    'error_type': 'ModuleNotFoundError',
                    'error_message': "No module named 'pandas'",
                    'solution_preview': 'pip install pandas'
                },
                'similarity_score': 0.85
            }
        ]
    }
    
    print("\n🎯 해결책 생성 중...\n")
    solution = llm.generate_solution(test_context)
    
    print("=" * 60)
    print(solution)
    print("=" * 60)
