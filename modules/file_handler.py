"""
모듈 1: 파일 핸들러
코드 파일 읽기, 업로드 처리, 파일 타입 감지
"""

import os
from pathlib import Path
from typing import Dict, List, Optional


class FileHandler:
    """파일 및 코드 입력 처리"""
    
    SUPPORTED_EXTENSIONS = {
        '.py': 'python',
        '.html': 'html',
        '.js': 'javascript',
        '.css': 'css',
        '.json': 'json'
    }
    
    @staticmethod
    def detect_file_type(file_path: str) -> Optional[str]:
        """
        파일 확장자로 타입 감지
        
        Args:
            file_path: 파일 경로
            
        Returns:
            파일 타입 (python, html, javascript 등) 또는 None
        """
        ext = Path(file_path).suffix.lower()
        return FileHandler.SUPPORTED_EXTENSIONS.get(ext)
    
    @staticmethod
    def read_file(file_path: str) -> Dict[str, any]:
        """
        파일 읽기
        
        Args:
            file_path: 파일 경로
            
        Returns:
            {
                'success': bool,
                'content': str,
                'file_type': str,
                'file_name': str,
                'error': str (실패 시)
            }
        """
        try:
            # 파일 존재 확인
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'파일을 찾을 수 없습니다: {file_path}'
                }
            
            # 파일 타입 감지
            file_type = FileHandler.detect_file_type(file_path)
            if not file_type:
                return {
                    'success': False,
                    'error': f'지원하지 않는 파일 형식입니다: {Path(file_path).suffix}'
                }
            
            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'success': True,
                'content': content,
                'file_type': file_type,
                'file_name': os.path.basename(file_path),
                'file_path': file_path
            }
            
        except UnicodeDecodeError:
            return {
                'success': False,
                'error': 'UTF-8로 읽을 수 없는 파일입니다 (바이너리 파일일 수 있음)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'파일 읽기 실패: {str(e)}'
            }
    
    @staticmethod
    def read_directory(dir_path: str, recursive: bool = False) -> Dict[str, any]:
        """
        디렉토리 내 지원되는 모든 파일 읽기
        
        Args:
            dir_path: 디렉토리 경로
            recursive: 하위 디렉토리 포함 여부
            
        Returns:
            {
                'success': bool,
                'files': [파일 정보 리스트],
                'error': str (실패 시)
            }
        """
        try:
            if not os.path.isdir(dir_path):
                return {
                    'success': False,
                    'error': f'디렉토리가 아닙니다: {dir_path}'
                }
            
            files = []
            
            if recursive:
                # 재귀적으로 탐색
                for root, _, filenames in os.walk(dir_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        file_info = FileHandler.read_file(file_path)
                        if file_info['success']:
                            files.append(file_info)
            else:
                # 현재 디렉토리만
                for item in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, item)
                    if os.path.isfile(file_path):
                        file_info = FileHandler.read_file(file_path)
                        if file_info['success']:
                            files.append(file_info)
            
            return {
                'success': True,
                'files': files,
                'count': len(files)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'디렉토리 읽기 실패: {str(e)}'
            }
    
    @staticmethod
    def validate_code_input(code: str, file_type: str) -> Dict[str, any]:
        """
        코드 입력 유효성 검사
        
        Args:
            code: 코드 문자열
            file_type: 파일 타입
            
        Returns:
            {
                'valid': bool,
                'error': str (유효하지 않을 시)
            }
        """
        if not code or not code.strip():
            return {
                'valid': False,
                'error': '코드가 비어있습니다'
            }
        
        if file_type not in FileHandler.SUPPORTED_EXTENSIONS.values():
            return {
                'valid': False,
                'error': f'지원하지 않는 파일 타입입니다: {file_type}'
            }
        
        # 기본 크기 제한 (10MB)
        if len(code.encode('utf-8')) > 10 * 1024 * 1024:
            return {
                'valid': False,
                'error': '코드 크기가 너무 큽니다 (최대 10MB)'
            }
        
        return {'valid': True}
