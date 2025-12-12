"""
고급 분석 엔진 모듈 - Ruff, Pylint, mypy, Bandit 통합
"""

import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


class AdvancedAnalyzer:
    """고급 코드 분석 엔진 통합"""
    
    @staticmethod
    def check_engine_available(engine: str) -> bool:
        """분석 엔진 설치 여부 확인"""
        try:
            subprocess.run([engine, '--version'], 
                         capture_output=True, 
                         timeout=2)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    @staticmethod
    def run_ruff(file_path: str, auto_fix: bool = False) -> Dict[str, Any]:
        """
        Ruff 린터 실행
        
        Args:
            file_path: 분석할 파일 경로
            auto_fix: 자동 수정 여부
        
        Returns:
            분석 결과
        """
        if not AdvancedAnalyzer.check_engine_available('ruff'):
            return {'available': False, 'error': 'Ruff not installed'}
        
        try:
            # Ruff check
            cmd = ['ruff', 'check', file_path, '--output-format=json']
            if auto_fix:
                cmd.append('--fix')
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            
            issues = []
            if result.stdout:
                try:
                    ruff_output = json.loads(result.stdout)
                    for issue in ruff_output:
                        issues.append({
                            'engine': 'ruff',
                            'file': issue.get('filename', file_path),
                            'line': issue.get('location', {}).get('row'),
                            'column': issue.get('location', {}).get('column'),
                            'code': issue.get('code'),
                            'message': issue.get('message'),
                            'severity': 'warning',
                            'fixable': issue.get('fix') is not None
                        })
                except json.JSONDecodeError:
                    pass
            
            return {
                'available': True,
                'success': result.returncode == 0,
                'issues': issues,
                'fixed': auto_fix
            }
            
        except Exception as e:
            return {'available': True, 'success': False, 'error': str(e)}
    
    @staticmethod
    def run_pylint(file_path: str) -> Dict[str, Any]:
        """
        Pylint 분석 실행
        
        Args:
            file_path: 분석할 파일 경로
        
        Returns:
            분석 결과
        """
        if not AdvancedAnalyzer.check_engine_available('pylint'):
            return {'available': False, 'error': 'Pylint not installed'}
        
        try:
            result = subprocess.run(
                ['pylint', file_path, '--output-format=json', '--reports=n'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            issues = []
            if result.stdout:
                try:
                    pylint_output = json.loads(result.stdout)
                    for issue in pylint_output:
                        # Pylint severity mapping
                        severity_map = {
                            'error': 'error',
                            'warning': 'warning',
                            'refactor': 'info',
                            'convention': 'info',
                            'info': 'info'
                        }
                        
                        issues.append({
                            'engine': 'pylint',
                            'file': issue.get('path', file_path),
                            'line': issue.get('line'),
                            'column': issue.get('column'),
                            'code': issue.get('message-id'),
                            'symbol': issue.get('symbol'),
                            'message': issue.get('message'),
                            'severity': severity_map.get(issue.get('type', 'info'), 'info')
                        })
                except json.JSONDecodeError:
                    pass
            
            # Pylint score
            score = None
            if result.stderr:
                # Extract score from stderr
                import re
                score_match = re.search(r'Your code has been rated at ([\d.]+)/10', result.stderr)
                if score_match:
                    score = float(score_match.group(1))
            
            return {
                'available': True,
                'success': True,
                'issues': issues,
                'score': score
            }
            
        except Exception as e:
            return {'available': True, 'success': False, 'error': str(e)}
    
    @staticmethod
    def run_mypy(file_path: str) -> Dict[str, Any]:
        """
        mypy 타입 체크 실행
        
        Args:
            file_path: 분석할 파일 경로
        
        Returns:
            분석 결과
        """
        if not AdvancedAnalyzer.check_engine_available('mypy'):
            return {'available': False, 'error': 'mypy not installed'}
        
        try:
            result = subprocess.run(
                ['mypy', file_path, '--show-column-numbers', '--no-error-summary'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            issues = []
            if result.stdout:
                # Parse mypy output (line:col: severity: message)
                for line in result.stdout.strip().split('\n'):
                    if ':' in line and file_path in line:
                        parts = line.split(':', 4)
                        if len(parts) >= 4:
                            issues.append({
                                'engine': 'mypy',
                                'file': file_path,
                                'line': int(parts[1]) if parts[1].isdigit() else None,
                                'column': int(parts[2]) if parts[2].isdigit() else None,
                                'severity': parts[3].strip().lower() if len(parts) > 3 else 'error',
                                'message': parts[4].strip() if len(parts) > 4 else parts[3].strip()
                            })
            
            return {
                'available': True,
                'success': result.returncode == 0,
                'issues': issues
            }
            
        except Exception as e:
            return {'available': True, 'success': False, 'error': str(e)}
    
    @staticmethod
    def run_bandit(file_path: str) -> Dict[str, Any]:
        """
        Bandit 보안 스캔 실행
        
        Args:
            file_path: 분석할 파일 경로
        
        Returns:
            분석 결과
        """
        if not AdvancedAnalyzer.check_engine_available('bandit'):
            return {'available': False, 'error': 'Bandit not installed'}
        
        try:
            result = subprocess.run(
                ['bandit', file_path, '-f', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            issues = []
            if result.stdout:
                try:
                    bandit_output = json.loads(result.stdout)
                    for issue in bandit_output.get('results', []):
                        # Bandit severity mapping
                        severity_map = {
                            'HIGH': 'error',
                            'MEDIUM': 'warning',
                            'LOW': 'info'
                        }
                        
                        issues.append({
                            'engine': 'bandit',
                            'file': file_path,
                            'line': issue.get('line_number'),
                            'code': issue.get('test_id'),
                            'message': issue.get('issue_text'),
                            'severity': severity_map.get(issue.get('issue_severity', 'LOW'), 'info'),
                            'confidence': issue.get('issue_confidence', 'UNDEFINED'),
                            'cwe': issue.get('cwe', {}).get('id')
                        })
                except json.JSONDecodeError:
                    pass
            
            return {
                'available': True,
                'success': result.returncode in [0, 1],  # Bandit returns 1 when issues found
                'issues': issues
            }
            
        except Exception as e:
            return {'available': True, 'success': False, 'error': str(e)}
    
    @staticmethod
    def comprehensive_analysis(file_path: str, 
                              engines: List[str] = ['all'],
                              auto_fix: bool = False) -> Dict[str, Any]:
        """
        모든 엔진을 사용한 종합 분석
        
        Args:
            file_path: 분석할 파일 경로
            engines: 사용할 엔진 리스트 (기본값: ['all'])
            auto_fix: Ruff 자동 수정 여부
        
        Returns:
            종합 분석 결과
        """
        all_engines = ['ruff', 'pylint', 'mypy', 'bandit']
        selected_engines = all_engines if 'all' in engines else engines
        
        results = {
            'file': file_path,
            'engines': {},
            'summary': {
                'total_issues': 0,
                'by_severity': {'error': 0, 'warning': 0, 'info': 0},
                'by_engine': {}
            },
            'all_issues': []
        }
        
        # Run each engine
        if 'ruff' in selected_engines:
            ruff_result = AdvancedAnalyzer.run_ruff(file_path, auto_fix)
            results['engines']['ruff'] = ruff_result
            if ruff_result.get('available') and ruff_result.get('issues'):
                results['all_issues'].extend(ruff_result['issues'])
        
        if 'pylint' in selected_engines:
            pylint_result = AdvancedAnalyzer.run_pylint(file_path)
            results['engines']['pylint'] = pylint_result
            if pylint_result.get('available') and pylint_result.get('issues'):
                results['all_issues'].extend(pylint_result['issues'])
        
        if 'mypy' in selected_engines:
            mypy_result = AdvancedAnalyzer.run_mypy(file_path)
            results['engines']['mypy'] = mypy_result
            if mypy_result.get('available') and mypy_result.get('issues'):
                results['all_issues'].extend(mypy_result['issues'])
        
        if 'bandit' in selected_engines:
            bandit_result = AdvancedAnalyzer.run_bandit(file_path)
            results['engines']['bandit'] = bandit_result
            if bandit_result.get('available') and bandit_result.get('issues'):
                results['all_issues'].extend(bandit_result['issues'])
        
        # Calculate summary
        results['summary']['total_issues'] = len(results['all_issues'])
        
        for issue in results['all_issues']:
            severity = issue.get('severity', 'info')
            if severity in results['summary']['by_severity']:
                results['summary']['by_severity'][severity] += 1
            
            engine = issue.get('engine')
            if engine:
                results['summary']['by_engine'][engine] = results['summary']['by_engine'].get(engine, 0) + 1
        
        # Sort issues by severity
        severity_order = {'error': 0, 'warning': 1, 'info': 2}
        results['all_issues'].sort(key=lambda x: (
            severity_order.get(x.get('severity', 'info'), 999),
            x.get('line', 9999)
        ))
        
        return results
