"""
프로젝트 스캐너 모듈 - 배치 분석 및 디렉토리 스캔
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from .file_handler import FileHandler
from .code_validator import CodeValidator
from .code_executor import CodeExecutor
from .error_analyzer import ErrorAnalyzer


class ProjectScanner:
    """프로젝트 스캐너 - 여러 파일 및 디렉토리 분석"""
    
    @staticmethod
    def scan_directory(directory: str, extensions: List[str] = ['.py'], recursive: bool = False) -> List[str]:
        """
        디렉토리를 스캔하여 지정된 확장자의 파일 목록 반환
        
        Args:
            directory: 스캔할 디렉토리 경로
            extensions: 포함할 파일 확장자 리스트 (기본값: ['.py'])
            recursive: 하위 디렉토리 포함 여부 (기본값: False)
        
        Returns:
            파일 경로 리스트
        """
        directory_path = Path(directory)
        
        if not directory_path.exists():
            raise ValueError(f"디렉토리를 찾을 수 없습니다: {directory}")
        
        if not directory_path.is_dir():
            raise ValueError(f"디렉토리가 아닙니다: {directory}")
        
        files = []
        
        if recursive:
            # 재귀적으로 모든 하위 디렉토리 검색
            for ext in extensions:
                files.extend(directory_path.rglob(f"*{ext}"))
        else:
            # 현재 디렉토리만 검색
            for ext in extensions:
                files.extend(directory_path.glob(f"*{ext}"))
        
        # Path 객체를 문자열로 변환하고 정렬
        return sorted([str(f) for f in files])
    
    @staticmethod
    def analyze_multiple_files(file_list: List[str], save_history: bool = False) -> Dict[str, Any]:
        """
        여러 파일을 분석하여 결과 요약 반환
        
        Args:
            file_list: 분석할 파일 경로 리스트
            save_history: DB에 저장 여부
        
        Returns:
            분석 결과 딕셔너리
        """
        results = {
            'total_files': len(file_list),
            'analyzed': 0,
            'success': 0,
            'errors': 0,
            'files_with_errors': [],
            'files_without_errors': [],
            'error_types': {},
            'details': []
        }
        
        for filepath in file_list:
            try:
                # 파일 읽기
                file_result = FileHandler.read_file(filepath)
                
                if not file_result['success']:
                    results['details'].append({
                        'file': filepath,
                        'status': 'read_error',
                        'error': file_result.get('error', 'Unknown')
                    })
                    continue
                
                code = file_result['content']
                
                # 정적 분석
                validation = CodeValidator.full_validation(code)
                
                file_analysis = {
                    'file': filepath,
                    'validation': validation,
                    'execution': None,
                    'error_analysis': None
                }
                
                # 코드 실행 및 에러 분석
                if validation['overall_valid']:
                    exec_result = CodeExecutor.safe_execute(code)
                    file_analysis['execution'] = exec_result
                    
                    if exec_result['success']:
                        results['success'] += 1
                        results['files_without_errors'].append(filepath)
                        file_analysis['status'] = 'success'
                    else:
                        # 에러 발생
                        if exec_result['stderr']:
                            error_analysis = ErrorAnalyzer.analyze_error(
                                exec_result['stderr'], 
                                code
                            )
                            file_analysis['error_analysis'] = error_analysis
                            
                            # 에러 타입별 분류
                            error_type = error_analysis.get('error_type', 'Unknown')
                            results['error_types'][error_type] = results['error_types'].get(error_type, 0) + 1
                        
                        results['errors'] += 1
                        results['files_with_errors'].append(filepath)
                        file_analysis['status'] = 'error'
                else:
                    # 정적 분석 실패
                    results['errors'] += 1
                    results['files_with_errors'].append(filepath)
                    file_analysis['status'] = 'validation_failed'
                    
                    # 정적 분석 에러도 카운트
                    if not validation.get('syntax', {}).get('valid', True):
                        results['error_types']['SyntaxError'] = results['error_types'].get('SyntaxError', 0) + 1
                    
                    missing_modules = validation.get('imports', {}).get('availability', {}).get('missing', [])
                    if missing_modules:
                        results['error_types']['ModuleNotFoundError'] = results['error_types'].get('ModuleNotFoundError', 0) + 1
                
                results['analyzed'] += 1
                results['details'].append(file_analysis)
                
            except Exception as e:
                results['details'].append({
                    'file': filepath,
                    'status': 'exception',
                    'error': str(e)
                })
        
        return results
