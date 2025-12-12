"""
자동 코드 수정 모듈
"""

import re
from typing import Dict, List, Tuple


class CodeFixer:
    """코드 자동 수정"""
    
    @staticmethod
    def suggest_fixes(code: str, error_analysis: Dict) -> List[Dict]:
        """
        에러 분석 결과를 바탕으로 수정 제안
        
        Args:
            code: 원본 코드
            error_analysis: ErrorAnalyzer.analyze_error() 결과
            
        Returns:
            수정 제안 리스트
        """
        fixes = []
        error_type = error_analysis.get('error_type', '')
        error_message = error_analysis.get('error_message', '')
        
        # 1. Import 에러 (모듈명 오타)
        if error_type == 'ModuleNotFoundError':
            import_fix = CodeFixer._fix_import_error(code, error_message)
            if import_fix:
                fixes.append(import_fix)
        
        # 2. NameError (변수명 오타)
        elif error_type == 'NameError':
            name_fix = CodeFixer._fix_name_error(code, error_message)
            if name_fix:
                fixes.append(name_fix)
        
        # 3. SyntaxError
        elif error_type == 'SyntaxError':
            syntax_fix = CodeFixer._fix_syntax_error(code, error_analysis)
            if syntax_fix:
                fixes.append(syntax_fix)
        
        return fixes
    
    @staticmethod
    def _fix_import_error(code: str, error_message: str) -> Dict:
        """Import 에러 수정"""
        # "No module named 'numpyy'" -> "numpyy"
        match = re.search(r"No module named ['\"](\w+)['\"]", error_message)
        if not match:
            return None
        
        wrong_module = match.group(1)
        
        # 일반적인 오타 매핑
        typo_map = {
            'numpyy': 'numpy',
            'pandass': 'pandas',
            'matplotlip': 'matplotlib',
            'requets': 'requests',
            'beatifulsoup': 'beautifulsoup4',
        }
        
        correct_module = typo_map.get(wrong_module)
        if correct_module:
            fixed_code = code.replace(f'import {wrong_module}', f'import {correct_module}')
            fixed_code = fixed_code.replace(f'from {wrong_module}', f'from {correct_module}')
            
            return {
                'type': 'import_fix',
                'description': f'"{wrong_module}" -> "{correct_module}"로 수정',
                'original': code,
                'fixed': fixed_code,
                'confidence': 0.9
            }
        
        return None
    
    @staticmethod
    def _fix_name_error(code: str, error_message: str) -> Dict:
        """NameError 수정"""
        # "name 'numpyy' is not defined"
        match = re.search(r"name ['\"](\w+)['\"] is not defined", error_message)
        if not match:
            return None
        
        wrong_name = match.group(1)
        
        # 코드에서 유사한 이름 찾기 (간단한 구현)
        defined_names = re.findall(r'\b(\w+)\s*=', code)
        imported_names = re.findall(r'import\s+(\w+)', code)
        all_names = set(defined_names + imported_names)
        
        # 레벤슈타인 거리로 유사한 이름 찾기 (간단 버전)
        similar = CodeFixer._find_similar_name(wrong_name, all_names)
        
        if similar:
            fixed_code = re.sub(r'\b' + wrong_name + r'\b', similar, code)
            return {
                'type': 'name_fix',
                'description': f'"{wrong_name}" -> "{similar}"로 수정 (추측)',
                'original': code,
                'fixed': fixed_code,
                'confidence': 0.7
            }
        
        return None
    
    @staticmethod
    def _fix_syntax_error(code: str, error_analysis: Dict) -> Dict:
        """SyntaxError 수정 (제한적)"""
        # 간단한 경우만 처리
        error_msg = error_analysis.get('error_message', '').lower()
        
        # 콜론 누락
        if 'expected' in error_msg and ':' in error_msg:
            # TODO: 더 정교한 구현 필요
            pass
        
        return None
    
    @staticmethod
    def _find_similar_name(target: str, candidates: set) -> str:
        """유사한 이름 찾기 (간단한 레벤슈타인 거리)"""
        if not candidates:
            return None
        
        def levenshtein(s1, s2):
            if len(s1) < len(s2):
                return levenshtein(s2, s1)
            if len(s2) == 0:
                return len(s1)
            
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        # 거리가 2 이하인 것만
        candidates_with_distance = [(name, levenshtein(target.lower(), name.lower())) 
                                     for name in candidates]
        candidates_with_distance = [(name, dist) for name, dist in candidates_with_distance if dist <= 2]
        
        if not candidates_with_distance:
            return None
        
        # 가장 가까운 것
        return min(candidates_with_distance, key=lambda x: x[1])[0]
    
    @staticmethod
    def generate_diff(original: str, fixed: str) -> str:
        """Diff 생성 (간단한 라인 기반)"""
        original_lines = original.splitlines()
        fixed_lines = fixed.splitlines()
        
        diff_lines = []
        max_len = max(len(original_lines), len(fixed_lines))
        
        for i in range(max_len):
            orig = original_lines[i] if i < len(original_lines) else ''
            fix = fixed_lines[i] if i < len(fixed_lines) else ''
            
            if orig != fix:
                if orig:
                    diff_lines.append(f'- {orig}')
                if fix:
                    diff_lines.append(f'+ {fix}')
            else:
                diff_lines.append(f'  {orig}')
        
        return '\n'.join(diff_lines)
