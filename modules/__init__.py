"""
에러 분석기 - 통합 모듈
4개 핵심 모듈을 통합하여 사용
"""

from modules.file_handler import FileHandler
from modules.code_validator import CodeValidator
from modules.code_executor import CodeExecutor
from modules.error_analyzer import ErrorAnalyzer


class ErrorAnalyzerIntegrated:
    """통합 에러 분석 시스템"""
    
    @staticmethod
    def analyze_file(file_path: str, execute: bool = True) -> dict:
        """
        파일 전체 분석 (읽기 → 검증 → 실행 → 에러 분석)
        
        Args:
            file_path: 분석할 파일 경로
            execute: 실행 여부 (False면 정적 분석만)
            
        Returns:
            종합 분석 결과
        """
        result = {
            'file_path': file_path,
            'stages': {}
        }
        
        print(f"\n{'='*60}")
        print(f"📂 파일 분석: {file_path}")
        print(f"{'='*60}\n")
        
        # Stage 1: 파일 읽기
        print("1️⃣ 파일 읽기...")
        file_result = FileHandler.read_file(file_path)
        result['stages']['file_read'] = file_result
        
        if not file_result['success']:
            print(f"   ❌ 실패: {file_result['error']}")
            return result
        
        print(f"   ✅ 성공 ({file_result['file_type']})")
        code = file_result['content']
        
        # Stage 2: 코드 검증 (Python만)
        if file_result['file_type'] == 'python':
            print("\n2️⃣ 코드 검증...")
            validation_result = CodeValidator.full_validation(code)
            result['stages']['validation'] = validation_result
            
            # Syntax
            if validation_result['syntax']['valid']:
                print("   ✅ Syntax 올바름")
            else:
                print(f"   ❌ Syntax 에러: {validation_result['syntax']['error']}")
                return result
            
            # Imports
            if validation_result['imports']:
                missing = validation_result['imports']['availability']['missing']
                if missing:
                    print(f"   ⚠️ 없는 패키지: {', '.join(missing)}")
                else:
                    print("   ✅ 모든 패키지 설치됨")
        
        # Stage 3: 실행
        if execute and file_result['file_type'] == 'python':
            print("\n3️⃣ 코드 실행...")
            exec_result = CodeExecutor.execute_python_code(code)
            result['stages']['execution'] = exec_result
            
            if exec_result['success']:
                print(f"   ✅ 성공 ({exec_result['execution_time']:.2f}초)")
                if exec_result['stdout']:
                    print(f"\n📤 출력:\n{exec_result['stdout']}")
            else:
                print(f"   ❌ 실행 실패")
                
                # Stage 4: 에러 분석
                if exec_result['stderr']:
                    print("\n4️⃣ 에러 분석...")
                    error_analysis = ErrorAnalyzer.analyze_error(exec_result['stderr'], code)
                    result['stages']['error_analysis'] = error_analysis
                    
                    print(f"\n{ErrorAnalyzer.format_analysis_report(error_analysis)}")
        
        print(f"\n{'='*60}")
        print("분석 완료")
        print(f"{'='*60}\n")
        
        return result
    
    @staticmethod
    def analyze_code_string(code: str, file_type: str = 'python') -> dict:
        """
        코드 문자열 분석
        
        Args:
            code: 코드 문자열
            file_type: 코드 타입
            
        Returns:
            분석 결과
        """
        result = {
            'code_length': len(code),
            'file_type': file_type,
            'stages': {}
        }
        
        print(f"\n{'='*60}")
        print(f"📝 코드 분석 ({file_type})")
        print(f"{'='*60}\n")
        
        # 입력 검증
        validation = FileHandler.validate_code_input(code, file_type)
        if not validation['valid']:
            print(f"❌ 입력 검증 실패: {validation['error']}")
            result['input_valid'] = False
            return result
        
        result['input_valid'] = True
        
        # Python 코드 분석
        if file_type == 'python':
            print("1️⃣ 코드 검증...")
            validation_result = CodeValidator.full_validation(code)
            result['stages']['validation'] = validation_result
            
            if not validation_result['syntax']['valid']:
                print(f"   ❌ Syntax 에러: {validation_result['syntax']['error']}")
                return result
            
            print("   ✅ Syntax 올바름")
            
            # 실행
            print("\n2️⃣ 코드 실행...")
            exec_result = CodeExecutor.execute_python_code(code)
            result['stages']['execution'] = exec_result
            
            if exec_result['success']:
                print(f"   ✅ 성공")
                if exec_result['stdout']:
                    print(f"\n📤 출력:\n{exec_result['stdout']}")
            else:
                print(f"   ❌ 실행 실패")
                
                # 에러 분석
                if exec_result['stderr']:
                    print("\n3️⃣ 에러 분석...")
                    error_analysis = ErrorAnalyzer.analyze_error(exec_result['stderr'], code)
                    result['stages']['error_analysis'] = error_analysis
                    
                    print(f"\n{ErrorAnalyzer.format_analysis_report(error_analysis)}")
        
        print(f"\n{'='*60}\n")
        
        return result


# CLI 테스트
if __name__ == '__main__':
    import sys
    
    print("\n" + "="*60)
    print("🔍 Python Error Analyzer - CLI 테스트")
    print("="*60)
    
    # 테스트 코드 1: Import 에러
    test_code1 = """
import numpyy
print(numpyy.array([1, 2, 3]))
"""
    
    analyzer = ErrorAnalyzerIntegrated()
    analyzer.analyze_code_string(test_code1, 'python')
    
    # 테스트 코드 2: 정상 코드
    test_code2 = """
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
print(greet("Python"))
"""
    
    analyzer.analyze_code_string(test_code2, 'python')
