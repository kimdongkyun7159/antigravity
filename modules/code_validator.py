"""
모듈 2: 코드 검증기
Python 코드의 syntax, import, 일반적인 오류 사전 탐지
"""

import ast
import sys
from typing import Dict, List, Optional


class CodeValidator:
    """Python 코드 정적 분석 및 검증"""
    
    @staticmethod
    def validate_syntax(code: str) -> Dict[str, any]:
        """
        Python 코드 syntax 검증
        
        Args:
            code: Python 코드 문자열
            
        Returns:
            {
                'valid': bool,
                'error': str (에러 메시지),
                'line': int (에러 라인),
                'error_type': str
            }
        """
        try:
            ast.parse(code)
            return {
                'valid': True,
                'message': 'Syntax가 올바릅니다'
            }
        except SyntaxError as e:
            return {
                'valid': False,
                'error': str(e.msg),
                'line': e.lineno,
                'offset': e.offset,
                'error_type': 'SyntaxError',
                'text': e.text
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @staticmethod
    def extract_imports(code: str) -> Dict[str, any]:
        """
        코드에서 import 문 추출
        
        Args:
            code: Python 코드
            
        Returns:
            {
                'success': bool,
                'imports': [모듈 이름 리스트],
                'from_imports': {module: [names]}
            }
        """
        try:
            tree = ast.parse(code)
            imports = []
            from_imports = {}
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    names = [alias.name for alias in node.names]
                    from_imports[module] = names
            
            return {
                'success': True,
                'imports': imports,
                'from_imports': from_imports
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def check_imports_available(imports: List[str]) -> Dict[str, any]:
        """
        import된 모듈들이 설치되어 있는지 확인
        
        Args:
            imports: 모듈 이름 리스트
            
        Returns:
            {
                'all_available': bool,
                'missing': [없는 모듈 리스트],
                'available': [있는 모듈 리스트]
            }
        """
        missing = []
        available = []
        
        for module_name in imports:
            # 서브모듈 처리 (예: os.path -> os)
            base_module = module_name.split('.')[0]
            
            try:
                __import__(base_module)
                available.append(module_name)
            except ImportError:
                missing.append(module_name)
        
        return {
            'all_available': len(missing) == 0,
            'missing': missing,
            'available': available
        }
    
    @staticmethod
    def detect_common_issues(code: str) -> List[Dict[str, any]]:
        """
        일반적인 코딩 오류 탐지
        
        Args:
            code: Python 코드
            
        Returns:
            이슈 리스트
        """
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # 1. 사용하지 않는 변수 탐지
            # 2. 정의되지 않은 변수 사용 탐지
            # 3. 들여쓰기 문제 (이미 syntax에서 잡힘)
            
            # 간단한 체크: print 함수 없이 한글 사용
            if '한글' in code and 'print' not in code:
                issues.append({
                    'type': 'suggestion',
                    'message': '한글이 포함되어 있지만 출력문이 없습니다. print()를 사용하세요.',
                    'severity': 'low'
                })
            
            # TODO: 더 정교한 분석 추가
            
        except:
            pass
        
        return issues
    
    @staticmethod
    def full_validation(code: str) -> Dict[str, any]:
        """
        전체 검증 (syntax + imports + 일반 이슈)
        
        Args:
            code: Python 코드
            
        Returns:
            종합 검증 결과
        """
        result = {
            'overall_valid': True,
            'syntax': None,
            'imports': None,
            'issues': []
        }
        
        # 1. Syntax 검증
        syntax_result = CodeValidator.validate_syntax(code)
        result['syntax'] = syntax_result
        
        if not syntax_result['valid']:
            result['overall_valid'] = False
            return result
        
        # 2. Import 검증
        import_result = CodeValidator.extract_imports(code)
        if import_result['success']:
            all_imports = import_result['imports'] + list(import_result['from_imports'].keys())
            availability = CodeValidator.check_imports_available(all_imports)
            result['imports'] = {
                'extracted': import_result,
                'availability': availability
            }
            
            if not availability['all_available']:
                result['overall_valid'] = False
        
        # 3. 일반 이슈 탐지
        result['issues'] = CodeValidator.detect_common_issues(code)
        
        return result
