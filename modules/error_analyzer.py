"""
모듈 4: 에러 분석기
실행 에러 캡처, 분류, 원인 분석, 해결책 제시
"""

import re
import traceback
from typing import Dict, List, Optional


class ErrorAnalyzer:
    """에러 분석 및 해결책 제시"""
    
    # 일반적인 에러 패턴과 해결책
    ERROR_PATTERNS = {
        'ModuleNotFoundError': {
            'pattern': r"No module named '(\w+)'",
            'description': '필요한 패키지가 설치되지 않았습니다',
            'solution_template': 'pip install {package}'
        },
        'ImportError': {
            'pattern': r"cannot import name '(\w+)' from '(\w+)'",
            'description': '모듈에서 해당 이름을 import할 수 없습니다',
            'solutions': [
                '철자가 올바른지 확인하세요',
                '해당 함수/클래스가 실제로 존재하는지 확인하세요',
                '패키지 버전이 호환되는지 확인하세요'
            ]
        },
        'NameError': {
            'pattern': r"name '(\w+)' is not defined",
            'description': '변수 또는 함수가 정의되지 않았습니다',
            'solutions': [
                '변수/함수 이름의 철자를 확인하세요',
                '변수를 사용하기 전에 정의했는지 확인하세요',
                'import문이 누락되지 않았는지 확인하세요'
            ]
        },
        'SyntaxError': {
            'pattern': r'invalid syntax',
            'description': '문법 오류가 있습니다',
            'solutions': [
                '괄호가 제대로 닫혔는지 확인하세요',
                '콜론(:)이 누락되지 않았는지 확인하세요',
                '들여쓰기가 올바른지 확인하세요',
                '따옴표가 제대로 닫혔는지 확인하세요'
            ]
        },
        'IndentationError': {
            'pattern': r'unexpected indent|expected an indented block',
            'description': '들여쓰기 오류',
            'solutions': [
                '들여쓰기를 일관되게 사용하세요 (탭 또는 스페이스 4칸)',
                '함수/클래스 정의 후 콜론(:) 다음 줄은 들여쓰기 해야 합니다',
                '같은 블록 내에서 들여쓰기 레벨을 맞추세요'
            ]
        },
        'TypeError': {
            'pattern': r"unsupported operand type|'(\w+)' object",
            'description': '타입이 맞지 않습니다',
            'solutions': [
                '변수의 타입을 확인하세요 (int, str, list 등)',
                '타입 변환이 필요한지 확인하세요 (예: str()int())',
                '해당 연산이 그 타입에서 지원되는지 확인하세요'
            ]
        },
        'AttributeError': {
            'pattern': r"'(\w+)' object has no attribute '(\w+)'",
            'description': '객체가 해당 속성/메서드를 가지고 있지 않습니다',
            'solutions': [
                '속성/메서드 이름의 철자를 확인하세요',
                '객체 타입이 올바른지 확인하세요',
                '해당 버전에서 지원하는 기능인지 확인하세요'
            ]
        },
        'IndexError': {
            'pattern': r'list index out of range',
            'description': '리스트 인덱스가 범위를 벗어났습니다',
            'solutions': [
                '리스트의 길이를 확인하세요 (len())',
                '인덱스가 0부터 시작함을 확인하세요',
                '빈 리스트가 아닌지 확인하세요'
            ]
        }
    }
    
    @staticmethod
    def analyze_error(stderr: str, code: str = '') -> Dict[str, any]:
        """
        에러 메시지 분석
        
        Args:
            stderr: 에러 출력 (traceback 포함)
            code: 원본 코드 (선택)
            
        Returns:
            {
                'error_detected': bool,
                'error_type': str,
                'error_message': str,
                'line_number': int,
                'description': str,
                'solutions': [해결책 리스트],
                'severity': str (low/medium/high)
            }
        """
        if not stderr or not stderr.strip():
            return {
                'error_detected': False,
                'message': '에러가 없습니다'
            }
        
        result = {
            'error_detected': True,
            'raw_error': stderr
        }
        
        # 에러 타입 추출
        error_type_match = re.search(r'(\w+Error):', stderr)
        if error_type_match:
            error_type = error_type_match.group(1)
            result['error_type'] = error_type
        else:
            result['error_type'] = 'Unknown'
        
        # 에러 메시지 추출
        error_lines = stderr.strip().split('\n')
        if error_lines:
            result['error_message'] = error_lines[-1]
        
        # 라인 번호 추출
        line_match = re.search(r'line (\d+)', stderr)
        if line_match:
            result['line_number'] = int(line_match.group(1))
        
        # 패턴 매칭으로 해결책 찾기
        error_type = result.get('error_type', 'Unknown')
        if error_type in ErrorAnalyzer.ERROR_PATTERNS:
            pattern_info = ErrorAnalyzer.ERROR_PATTERNS[error_type]
            result['description'] = pattern_info['description']
            
            # 구체적인 해결책 생성
            if 'solution_template' in pattern_info:
                # 에러 메시지에서 패키지 이름 추출
                match = re.search(pattern_info['pattern'], stderr)
                if match:
                    package = match.group(1)
                    specific_solution = pattern_info['solution_template'].format(package=package)
                    result['solutions'] = [specific_solution]
            elif 'solutions' in pattern_info:
                result['solutions'] = pattern_info['solutions']
        else:
            # 알려지지 않은 에러
            result['description'] = '알 수 없는 에러입니다'
            result['solutions'] = [
                '에러 메시지를 주의 깊게 읽어보세요',
                '온라인에서 에러 메시지를 검색해보세요',
                '관련 문서를 확인하세요'
            ]
        
        # 심각도 판단
        if error_type in ['SyntaxError', 'IndentationError']:
            result['severity'] = 'high'
        elif error_type in ['ModuleNotFoundError', 'ImportError', 'NameError']:
            result['severity'] = 'high'
        else:
            result['severity'] = 'medium'
        
        return result
    
    @staticmethod
    def format_analysis_report(analysis: Dict[str, any]) -> str:
        """
        분석 결과를 사람이 읽기 쉬운 형식으로 포맷
        
        Args:
            analysis: analyze_error() 결과
            
        Returns:
            포맷된 리포트 문자열
        """
        if not analysis.get('error_detected'):
            return "✅ 에러가 없습니다!"
        
        lines = []
        # lines.append("=" * 60)
        lines.append(f"🚨 {analysis.get('error_type', 'Error')} 발생")
        # lines.append("=" * 60)
        
        if 'line_number' in analysis:
            lines.append(f"📍 라인: {analysis['line_number']}")
        
        lines.append(f"\n❌ 에러 메시지:")
        lines.append(f"   {analysis.get('error_message', 'N/A')}")
        
        if 'description' in analysis:
            lines.append(f"\n📖 설명:")
            lines.append(f"   {analysis['description']}")
        
        if 'solutions' in analysis:
            lines.append(f"\n💡 해결 방법:")
            for i, solution in enumerate(analysis['solutions'], 1):
                lines.append(f"   {i}. {solution}")
        
        # lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    @staticmethod
    def suggest_code_fix(code: str, analysis: Dict[str, any]) -> Optional[str]:
        """
        에러 분석을 바탕으로 코드 수정 제안
        
        Args:
            code: 원본 코드
            analysis: 에러 분석 결과
            
        Returns:
            수정된 코드 (가능한 경우) 또는 None
        """
        error_type = analysis.get('error_type')
        
        # ImportError/ModuleNotFoundError - import 문 수정
        if error_type in ['ModuleNotFoundError', 'ImportError']:
            if 'solutions' in analysis and analysis['solutions']:
                # pip install 명령은 코드 수정이 아님
                if 'pip install' in analysis['solutions'][0]:
                    return None
        
        # TODO: 더 정교한 자동 수정 로직
        
        return None


# 테스트
if __name__ == '__main__':
    # 테스트 1: ModuleNotFoundError
    test_stderr1 = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    import numpyy
ModuleNotFoundError: No module named 'numpyy'"""
    
    print("=" * 60)
    print("테스트 1: ModuleNotFoundError")
    print("=" * 60)
    analysis1 = ErrorAnalyzer.analyze_error(test_stderr1)
    print(ErrorAnalyzer.format_analysis_report(analysis1))
    
    # 테스트 2: NameError
    test_stderr2 = """Traceback (most recent call last):
  File "test.py", line 3, in <module>
    print(resultado)
NameError: name 'resultado' is not defined"""
    
    print("\n" + "=" * 60)
    print("테스트 2: NameError")
    print("=" * 60)
    analysis2 = ErrorAnalyzer.analyze_error(test_stderr2)
    print(ErrorAnalyzer.format_analysis_report(analysis2))
