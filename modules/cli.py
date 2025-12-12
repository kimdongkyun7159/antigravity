"""
CLI 모듈 - 커맨드라인 인터페이스
"""

import argparse
import json
import sys
from pathlib import Path
from modules.file_handler import FileHandler
from modules.code_validator import CodeValidator
from modules.code_executor import CodeExecutor
from modules.error_analyzer import ErrorAnalyzer
from modules.error_database import ErrorDatabase
from modules.code_fixer import CodeFixer
from modules.project_scanner import ProjectScanner
from modules.pattern_learner import PatternLearner
from modules.advanced_analyzer import AdvancedAnalyzer
import shutil


class ErrorAnalyzerCLI:
    """CLI 인터페이스"""
    
    def __init__(self):
        self.db = ErrorDatabase()
    
    def analyze_file(self, filepath, output_format='text', save_history=True):
        """
        파일 분석
        
        Args:
            filepath: 분석할 파일 경로
            output_format: 'text' 또는 'json'
            save_history: DB에 저장 여부
        """
        try:
            # 파일 읽기
            file_result = FileHandler.read_file(filepath)
            
            if not file_result['success']:
                raise ValueError(file_result.get('error', 'File read failed'))
            
            code = file_result['content']
            
            # 정적 분석
            validation = CodeValidator.full_validation(code)
            
            result = {
                'file': str(filepath),
                'validation': validation,
                'execution': None,
                'error_analysis': None,
                'similar_errors': None
            }
            
            # 코드 실행
            if validation['overall_valid']:
                exec_result = CodeExecutor.safe_execute(code)
                result['execution'] = exec_result
                
                # 에러 분석
                if not exec_result['success'] and exec_result['stderr']:
                    error_analysis = ErrorAnalyzer.analyze_error(
                        exec_result['stderr'], 
                        code
                    )
                    result['error_analysis'] = error_analysis
                    
                    # 히스토리 저장
                    if save_history:
                        self.db.save_error(code, error_analysis)
                    
                    # 유사 에러 검색
                    similar_errors = self.db.find_similar_errors(error_analysis, limit=3)
                    if similar_errors:
                        result['similar_errors'] = similar_errors
            
            # 출력
            if output_format == 'json':
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                self._print_text_result(result)
            
            # 에러가 있으면 exit code 1
            has_error = (
                not validation['overall_valid'] or 
                (result['execution'] and not result['execution']['success'])
            )
            return 1 if has_error else 0
            
        except Exception as e:
            if output_format == 'json':
                print(json.dumps({'error': str(e)}, ensure_ascii=False))
            else:
                print(f"❌ 에러: {e}")
            return 1
    
    def _print_text_result(self, result):
        """텍스트 형식 결과 출력"""
        print("=" * 60)
        print(f"📄 파일: {result['file']}")
        print("=" * 60)
        
        # 정적 분석 결과
        validation = result['validation']
        if validation['overall_valid']:
            print("✅ 정적 분석: 통과")
        else:
            print("❌ 정적 분석: 실패")
            if validation.get('syntax') and not validation['syntax']['valid']:
                print(f"   - Syntax 에러: {validation['syntax'].get('error', 'Unknown')}")
            if validation.get('imports'):
                missing = validation['imports']['availability'].get('missing', [])
                if missing:
                    print(f"   - 없는 모듈: {', '.join(missing)}")
        
        # 실행 결과
        if result['execution']:
            exec_result = result['execution']
            if exec_result['success']:
                print("\n✅ 실행: 성공")
                if exec_result['stdout']:
                    print(f"\n출력:\n{exec_result['stdout']}")
            else:
                print("\n❌ 실행: 실패")
                if exec_result['stderr']:
                    print(f"\n에러:\n{exec_result['stderr']}")
        
        # 에러 분석
        if result['error_analysis']:
            analysis = result['error_analysis']
            print(f"\n🔍 에러 분석")
            print(f"   타입: {analysis.get('error_type', 'Unknown')}")
            print(f"   설명: {analysis.get('description', 'N/A')}")
            
            if analysis.get('solutions'):
                print(f"\n💡 해결 방법:")
                for i, sol in enumerate(analysis['solutions'], 1):
                    print(f"   {i}. {sol}")
        
        # 유사 에러
        if result['similar_errors']:
            print(f"\n📚 과거 유사 에러: {len(result['similar_errors'])}개")
        
        print("\n" + "=" * 60)
    
    def fix_file(self, filepath, show_diff=False, auto_apply=False):
        """
        파일의 에러를 자동 수정
        
        Args:
            filepath: 수정할 파일 경로
            show_diff: diff 표시 여부
            auto_apply: 자동 적용 여부
        """
        try:
            # 1. 파일 분석
            file_result = FileHandler.read_file(filepath)
            if not file_result['success']:
                raise ValueError(file_result.get('error', 'File read failed'))
            
            code = file_result['content']
            
            # 2. 에러 찾기
            validation = CodeValidator.full_validation(code)
            if validation['overall_valid']:
                exec_result = CodeExecutor.safe_execute(code)
                
                if exec_result['success']:
                    print("✅ 에러가 없습니다. 수정할 것이 없습니다.")
                    return 0
                
                # 에러 분석
                error_analysis = ErrorAnalyzer.analyze_error(
                    exec_result['stderr'], 
                    code
                )
            else:
                # 정적 분석 실패 - import 에러 등을 수정
                print("⚠️  정적 분석에서 문제 발견")
                
                # import 에러를 error_analysis 형식으로 변환
                missing_modules = validation.get('imports', {}).get('availability', {}).get('missing', [])
                if missing_modules:
                    error_analysis = {
                        'error_type': 'ModuleNotFoundError',
                        'error_message': f"No module named '{missing_modules[0]}'",
                        'description': f"'{missing_modules[0]}' 모듈을 찾을 수 없습니다",
                        'solutions': [f"pip install {missing_modules[0]}"],
                        'line_number': None,
                        'context': code
                    }
                else:
                    # 다른 정적 분석 실패 (syntax 에러 등)
                    syntax_error = validation.get('syntax', {}).get('error', '알 수 없는 에러')
                    print(f"❌ 수정 불가능한 에러입니다: {syntax_error}")
                    return 1
            
            # 3. 수정 제안 생성
            fixes = CodeFixer.suggest_fixes(code, error_analysis)
            
            if not fixes:
                print("💡 자동 수정 제안을 생성할 수 없습니다.")
                print(f"\n에러 타입: {error_analysis.get('error_type', 'Unknown')}")
                print(f"설명: {error_analysis.get('description', 'N/A')}")
                return 1
            
            # 4. 수정 제안 표시
            print("=" * 60)
            print(f"🔧 자동 수정 제안")
            print("=" * 60)
            
            for i, fix in enumerate(fixes, 1):
                print(f"\n[제안 {i}] {fix['description']}")
                print(f"   신뢰도: {fix['confidence'] * 100:.0f}%")
                
                if show_diff:
                    diff = CodeFixer.generate_diff(fix['original'], fix['fixed'])
                    print(f"\n{diff}")
            
            # 5. 적용
            if auto_apply:
                best_fix = max(fixes, key=lambda x: x['confidence'])
                
                # 백업
                backup_path = f"{filepath}.backup"
                shutil.copy(filepath, backup_path)
                print(f"\n💾 백업 생성: {backup_path}")
                
                # 적용
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(best_fix['fixed'])
                
                print(f"✅ 수정 적용 완료: {filepath}")
                print(f"   {best_fix['description']}")
            else:
                print("\n💡 --auto-apply 옵션을 사용하면 자동으로 수정합니다.")
            
            print("\n" + "=" * 60)
            return 0
            
        except Exception as e:
            print(f"❌ 에러: {e}")
            return 1
    
    def batch_analyze(self, files, output_format='text'):
        """
        여러 파일을 배치로 분석
        
        Args:
            files: 분석할 파일 경로 리스트
            output_format: 'text' 또는 'json'
        """
        try:
            print(f"📦 배치 분석 시작: {len(files)}개 파일")
            print("=" * 60)
            
            # 배치 분석 실행
            results = ProjectScanner.analyze_multiple_files(files)
            
            # 출력
            if output_format == 'json':
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                self._print_batch_result(results)
            
            return 1 if results['errors'] > 0 else 0
            
        except Exception as e:
            print(f"❌ 에러: {e}")
            return 1
    
    def scan_directory(self, directory, recursive=False, output_format='text'):
        """
        디렉토리를 스캔하여 분석
        
        Args:
            directory: 스캔할 디렉토리 경로
            recursive: 하위 디렉토리 포함 여부
            output_format: 'text' 또는 'json'
        """
        try:
            print(f"🔍 디렉토리 스캔: {directory}")
            if recursive:
                print("   (하위 디렉토리 포함)")
            print("=" * 60)
            
            # 디렉토리 스캔
            files = ProjectScanner.scan_directory(directory, recursive=recursive)
            
            if not files:
                print("⚠️  Python 파일을 찾을 수 없습니다.")
                return 0
            
            print(f"✅ {len(files)}개 파일 발견\n")
            
            # 배치 분석 실행
            results = ProjectScanner.analyze_multiple_files(files)
            
            # 출력
            if output_format == 'json':
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                self._print_batch_result(results)
            
            return 1 if results['errors'] > 0 else 0
            
        except Exception as e:
            print(f"❌ 에러: {e}")
            return 1
    
    def _print_batch_result(self, results):
        """배치 분석 결과 출력"""
        print("\n" + "=" * 60)
        print("📊 분석 결과 요약")
        print("=" * 60)
        
        print(f"총 파일 수: {results['total_files']}")
        print(f"분석 완료: {results['analyzed']}")
        print(f"✅ 성공: {results['success']}")
        print(f"❌ 에러: {results['errors']}")
        
        # 에러 타입별 통계
        if results['error_types']:
            print(f"\n🔍 에러 타입별 통계:")
            for error_type, count in sorted(results['error_types'].items(), key=lambda x: x[1], reverse=True):
                print(f"   - {error_type}: {count}개")
        
        # 에러가 있는 파일 목록
        if results['files_with_errors']:
            print(f"\n❌ 에러가 있는 파일 ({len(results['files_with_errors'])}개):")
            for filepath in results['files_with_errors'][:10]:  # 최대 10개만 표시
                print(f"   - {filepath}")
            
            if len(results['files_with_errors']) > 10:
                print(f"   ... 외 {len(results['files_with_errors']) - 10}개")
        
        # 성공한 파일 목록 (간략히)
        if results['files_without_errors']:
            print(f"\n✅ 에러 없는 파일: {len(results['files_without_errors'])}개")
        
        print("\n" + "=" * 60)
    
    def show_statistics(self, top=10, output_format='text'):
        """에러 통계 표시"""
        try:
            stats = PatternLearner.get_error_statistics(self.db, limit=top)
            
            if output_format == 'json':
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            else:
                print("=" * 60)
                print("📊 Error Analyzer 통계")
                print("=" * 60)
                print(f"\n총 에러 기록: {stats['total_errors']}개")
                
                if stats['error_types']:
                    print(f"\n🔍 에러 타입별 통계:")
                    for error_type, count in stats['error_types'].items():
                        print(f"   - {error_type}: {count}개")
                
                if stats['common_patterns']:
                    print(f"\n📈 자주 발생하는 패턴 (Top {len(stats['common_patterns'])}):")
                    for i, pattern in enumerate(stats['common_patterns'], 1):
                        print(f"   {i}. [{pattern['error_type']}] {pattern['error_message']}")
                        print(f"      발생 횟수: {pattern['count']}회")
                
                if stats['recent_errors']:
                    print(f"\n🕒 최근 에러 (Top {len(stats['recent_errors'])}):")
                    for error in stats['recent_errors']:
                        print(f"   - [{error['error_type']}] {error['error_message'][:60]}...")
                
                print("\n" + "=" * 60)
            
            return 0
        except Exception as e:
            print(f"❌ 에러: {e}")
            return 1
    
    def deep_analyze_file(self, filepath, engines=['all'], output_format='text', auto_fix=False):
        """
        고급 분석 엔진으로 파일 분석
        
        Args:
            filepath: 분석할 파일
            engines: 사용할 엔진 리스트
            output_format: 'text' 또는 'json'
            auto_fix: Ruff 자동 수정 여부
        """
        try:
            print(f"🔍 고급 분석 시작: {filepath}")
            print(f"   사용 엔진: {', '.join(engines) if 'all' not in engines else 'All (Ruff, Pylint, mypy, Bandit)'}")
            print("=" * 60)
            
            # 종합 분석 실행
            results = AdvancedAnalyzer.comprehensive_analysis(filepath, engines, auto_fix)
            
            if output_format == 'json':
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                self._print_deep_analysis(results)
            
            return 1 if results['summary']['total_issues'] > 0 else 0
            
        except Exception as e:
            print(f"❌ 에러: {e}")
            return 1
    
    def _print_deep_analysis(self, results):
        """고급 분석 결과 텍스트 출력"""
        print("\n" + "=" * 60)
        print("📊 분석 요약")
        print("=" * 60)
        
        summary = results['summary']
        print(f"총 이슈: {summary['total_issues']}개")
        
        if summary['by_severity']:
            print(f"\n심각도별:")
            print(f"   🔴 Error: {summary['by_severity'].get('error', 0)}개")
            print(f"   🟡 Warning: {summary['by_severity'].get('warning', 0)}개")
            print(f"   ℹ️  Info: {summary['by_severity'].get('info', 0)}개")
        
        if summary['by_engine']:
            print(f"\n엔진별:")
            for engine, count in summary['by_engine'].items():
                print(f"   - {engine}: {count}개")
        
        # Pylint score
        if 'pylint' in results['engines'] and results['engines']['pylint'].get('score'):
            print(f"\n📈 Pylint 점수: {results['engines']['pylint']['score']}/10")
        
        # 이슈 상세
        if results['all_issues']:
            print(f"\n" + "=" * 60)
            print("🔍 발견된 이슈 (심각도 순)")
            print("=" * 60)
            
            for i, issue in enumerate(results['all_issues'][:20], 1):  # 최대 20개만 표시
                severity_icon = {
                    'error': '🔴',
                    'warning': '🟡',
                    'info': 'ℹ️'
                }.get(issue.get('severity', 'info'), 'ℹ️')
                
                print(f"\n{i}. {severity_icon} [{issue.get('engine', 'unknown').upper()}] Line {issue.get('line', '?')}")
                if issue.get('code'):
                    print(f"   Code: {issue['code']}")
                print(f"   {issue.get('message', 'No message')}")
                
                if issue.get('fixable'):
                    print(f"   ✅ 자동 수정 가능")
            
            if len(results['all_issues']) > 20:
                print(f"\n   ... 외 {len(results['all_issues']) - 20}개 이슈")
        
        print("\n" + "=" * 60)


def main():
    """CLI 메인 함수"""
    parser = argparse.ArgumentParser(
        description='Error Analyzer - AI 코드 에러 분석 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='명령어')
    
    # analyze 명령
    analyze_parser = subparsers.add_parser('analyze', help='파일 분석')
    analyze_parser.add_argument('file', help='분석할 파일')
    analyze_parser.add_argument('--json', action='store_true', help='JSON 형식 출력')
    analyze_parser.add_argument('--no-save', action='store_true', help='히스토리 저장 안함')
    
    # fix 명령
    fix_parser = subparsers.add_parser('fix', help='파일 자동 수정')
    fix_parser.add_argument('file', help='수정할 파일')
    fix_parser.add_argument('--show-diff', action='store_true', help='diff 표시')
    fix_parser.add_argument('--auto-apply', action='store_true', help='자동 적용')
    
    # batch 명령
    batch_parser = subparsers.add_parser('batch', help='여러 파일 분석')
    batch_parser.add_argument('files', nargs='+', help='파일 목록')
    batch_parser.add_argument('--json', action='store_true', help='JSON 출력')
    
    # scan 명령
    scan_parser = subparsers.add_parser('scan', help='프로젝트 스캔')
    scan_parser.add_argument('directory', help='스캔할 디렉토리')
    scan_parser.add_argument('--recursive', action='store_true', help='하위 디렉토리 포함')
    scan_parser.add_argument('--json', action='store_true', help='JSON 출력')
    
    # stats 명령
    stats_parser = subparsers.add_parser('stats', help='에러 통계 조회')
    stats_parser.add_argument('--top', type=int, default=10, help='상위 N개 (기본값: 10)')
    stats_parser.add_argument('--json', action='store_true', help='JSON 출력')
    
    # deep-analyze 명령
    deep_parser = subparsers.add_parser('deep-analyze', help='고급 분석 (다중 엔진)')
    deep_parser.add_argument('file', help='분석할 파일')
    deep_parser.add_argument('--engines', nargs='+',
                            choices=['ruff', 'pylint', 'mypy', 'bandit', 'all'],
                            default=['all'], help='사용할 엔진 (기본값: all)')
    deep_parser.add_argument('--json', action='store_true', help='JSON 출력')
    deep_parser.add_argument('--fix', action='store_true', help='Ruff 자동 수정 적용')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    cli = ErrorAnalyzerCLI()
    
    if args.command == 'analyze':
        output_format = 'json' if args.json else 'text'
        save_history = not args.no_save
        return cli.analyze_file(args.file, output_format, save_history)
    
    elif args.command == 'fix':
        return cli.fix_file(args.file, args.show_diff, args.auto_apply)
    
    elif args.command == 'batch':
        output_format = 'json' if args.json else 'text'
        return cli.batch_analyze(args.files, output_format)
    
    elif args.command == 'scan':
        output_format = 'json' if args.json else 'text'
        return cli.scan_directory(args.directory, args.recursive, output_format)
    
    elif args.command == 'stats':
        output_format = 'json' if args.json else 'text'
        return cli.show_statistics(args.top, output_format)
    
    elif args.command == 'deep-analyze':
        output_format = 'json' if args.json else 'text'
        return cli.deep_analyze_file(args.file, args.engines, output_format, args.fix)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
