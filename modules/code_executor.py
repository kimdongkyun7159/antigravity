"""
모듈 3: 코드 실행기
안전한 환경에서 Python 코드 실행 및 출력/에러 캡처
"""

import subprocess
import tempfile
import os
import time
import sys
from typing import Dict, Optional


class CodeExecutor:
    """안전한 Python 코드 실행"""
    
    DEFAULT_TIMEOUT = 30  # 초
    
    @staticmethod
    def execute_python_code(code: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, any]:
        """
        Python 코드를 별도 프로세스에서 실행
        
        Args:
            code: 실행할 Python 코드
            timeout: 타임아웃 (초)
            
        Returns:
            {
                'success': bool,
                'stdout': str (표준 출력),
                'stderr': str (에러 출력),
                'exit_code': int,
                'execution_time': float (초),
                'timed_out': bool
            }
        """
        # 임시 파일에 코드 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            temp_file = f.name
            f.write(code)
        
        try:
            start_time = time.time()
            
            # subprocess로 실행
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode,
                'execution_time': execution_time,
                'timed_out': False
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'코드 실행이 {timeout}초를 초과하여 중단되었습니다.',
                'exit_code': -1,
                'execution_time': timeout,
                'timed_out': True
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'실행 중 오류: {str(e)}',
                'exit_code': -1,
                'execution_time': 0,
                'timed_out': False
            }
        finally:
            # 임시 파일 삭제
            try:
                os.unlink(temp_file)
            except:
                pass
    
    @staticmethod
    def execute_python_file(file_path: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, any]:
        """
        Python 파일 실행
        
        Args:
            file_path: Python 파일 경로
            timeout: 타임아웃 (초)
            
        Returns:
            실행 결과 (execute_python_code와 동일)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return CodeExecutor.execute_python_code(code, timeout)
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'파일 읽기 실패: {str(e)}',
                'exit_code': -1,
                'execution_time': 0,
                'timed_out': False
            }
    
    @staticmethod
    def safe_execute(code: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, any]:
        """
        안전 장치를 추가한 실행
        (위험한 코드 패턴 사전 차단)
        
        Args:
            code: Python 코드
            timeout: 타임아웃
            
        Returns:
            실행 결과
        """
        # 위험한 패턴 체크
        dangerous_patterns = [
            'os.system',
            'subprocess.call',
            'subprocess.Popen',
            'eval(',
            'exec(',
            '__import__',
            'open(',  # 파일 시스템 접근
            'rmdir',
            'unlink',
            'remove'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                return {
                    'success': False,
                    'stdout': '',
                    'stderr': f'⚠️ 보안: 위험한 코드 패턴이 감지되었습니다: {pattern}\n실행이 차단되었습니다.',
                    'exit_code': -1,
                    'execution_time': 0,
                    'timed_out': False,
                    'blocked': True
                }
        
        return CodeExecutor.execute_python_code(code, timeout)


# 테스트용
if __name__ == '__main__':
    import sys
    
    # 테스트 1: 정상 코드
    test_code1 = """
print("Hello, World!")
x = 10
y = 20
print(f"Sum: {x + y}")
"""
    
    print("=" * 60)
    print("테스트 1: 정상 코드")
    print("=" * 60)
    result1 = CodeExecutor.execute_python_code(test_code1)
    print(f"Success: {result1['success']}")
    print(f"Output:\n{result1['stdout']}")
    print(f"Error:\n{result1['stderr']}")
    
    # 테스트 2: 에러 코드
    test_code2 = """
import numpyy
print(numpyy.array([1, 2, 3]))
"""
    
    print("\n" + "=" * 60)
    print("테스트 2: Import 에러")
    print("=" * 60)
    result2 = CodeExecutor.execute_python_code(test_code2)
    print(f"Success: {result2['success']}")
    print(f"Error:\n{result2['stderr']}")
