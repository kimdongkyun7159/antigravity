"""
Flask 백엔드 - 최신 RESTful API
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys

# 모듈 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.file_handler import FileHandler
from modules.code_validator import CodeValidator
from modules.code_executor import CodeExecutor
from modules.error_analyzer import ErrorAnalyzer
from modules.error_database import ErrorDatabase
from modules.rag_orchestrator import RAGOrchestrator
from modules.config import Config

app = Flask(__name__)
CORS(app)  # CORS 활성화

# 설정
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = 'uploads'

# 업로드 폴더 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 데이터베이스 초기화
db = ErrorDatabase()

# RAG Orchestrator 초기화
try:
    rag_orchestrator = RAGOrchestrator(use_rag=Config.RAG_ENABLED)
    rag_available = rag_orchestrator.use_rag
except Exception as e:
    print(f"⚠️ RAG 초기화 실패: {e}")
    rag_orchestrator = None
    rag_available = False


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'success': True,
        'status': 'running',
        'version': '2.0.0',
        'rag_enabled': rag_available,
        'features': {
            'basic_analysis': True,
            'rag_analysis': rag_available,
            'vector_search': rag_available
        }
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """
    코드 분석 API
    
    Request Body:
        {
            "code": str,
            "file_type": str (optional, default: "python"),
            "execute": bool (optional, default: true)
        }
    
    Returns:
        {
            "success": bool,
            "analysis": {...},
            "error": str (if failed)
        }
    """
    try:
        data = request.get_json()
        
        # 입력 검증
        if not data or 'code' not in data:
            return jsonify({
                'success': False,
                'error': '코드가 제공되지 않았습니다'
            }), 400
        
        code = data['code']
        file_type = data.get('file_type', 'python')
        execute = data.get('execute', True)
        
        # 입력 유효성 검사
        validation = FileHandler.validate_code_input(code, file_type)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': validation['error']
            }), 400
        
        result = {
            'success': True,
            'file_type': file_type,
            'analysis': {}
        }
        
        # Python 코드 분석
        if file_type == 'python':
            # 1. 정적 분석
            validation_result = CodeValidator.full_validation(code)
            result['analysis']['validation'] = validation_result
            
            # Syntax 에러가 있으면 즉시 반환
            if not validation_result['syntax']['valid']:
                return jsonify(result)
            
            # 2. 실행 (옵션)
            if execute:
                exec_result = CodeExecutor.safe_execute(code)
                result['analysis']['execution'] = exec_result
                
                # 에러 분석
                if not exec_result['success'] and exec_result['stderr']:
                    error_analysis = ErrorAnalyzer.analyze_error(
                        exec_result['stderr'], 
                        code
                    )
                    result['analysis']['error_analysis'] = error_analysis
                    
                    # 히스토리 저장 (옵션)
                    save_history = data.get('save_history', True)
                    if save_history:
                        try:
                            db.save_error(code, error_analysis)
                        except Exception as e:
                            print(f"⚠️ DB 저장 실패: {e}")
                    
                    # 유사 에러 검색
                    try:
                        similar_errors = db.find_similar_errors(error_analysis, limit=3)
                        if similar_errors:
                            result['analysis']['similar_errors'] = similar_errors
                    except Exception as e:
                        print(f"⚠️ 유사 에러 검색 실패: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'서버 오류: {str(e)}'
        }), 500


@app.route('/api/analyze-rag', methods=['POST'])
def analyze_with_rag():
    """
    RAG 기반 코드 분석 API
    
    Request Body:
        {
            "code": str,
            "file_type": str (optional, default: "python")
        }
    
    Returns:
        {
            "success": bool,
            "rag_analysis": {...}
        }
    """
    try:
        # RAG 사용 불가능하면 에러
        if not rag_available or not rag_orchestrator:
            return jsonify({
                'success': False,
                'error': 'RAG 기능을 사용할 수 없습니다. Gemini API 키를 설정하세요.'
            }), 503
        
        data = request.get_json()
        
        # 입력 검증
        if not data or 'code' not in data:
            return jsonify({
                'success': False,
                'error': '코드가 제공되지 않았습니다'
            }), 400
        
        code = data['code']
        file_type = data.get('file_type', 'python')
        
        # 입력 유효성 검사
        validation = FileHandler.validate_code_input(code, file_type)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': validation['error']
            }), 400
        
        # RAG 분석 실행
        rag_result = rag_orchestrator.analyze_with_rag(code, file_type)
        
        return jsonify({
            'success': True,
            'rag_analysis': rag_result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'서버 오류: {str(e)}'
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    파일 업로드 및 분석
    
    Form Data:
        file: 파일
        execute: bool (optional)
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '파일이 없습니다'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '파일이 선택되지 않았습니다'
            }), 400
        
        # 파일 저장
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 파일 읽기
        file_result = FileHandler.read_file(filepath)
        
        if not file_result['success']:
            return jsonify(file_result), 400
        
        # 코드 분석 (위의 analyze_code와 동일한 로직)
        code = file_result['content']
        file_type = file_result['file_type']
        execute = request.form.get('execute', 'true').lower() == 'true'
        
        result = {
            'success': True,
            'file_name': filename,
            'file_type': file_type,
            'analysis': {}
        }
        
        if file_type == 'python':
            validation_result = CodeValidator.full_validation(code)
            result['analysis']['validation'] = validation_result
            
            if validation_result['syntax']['valid'] and execute:
                exec_result = CodeExecutor.safe_execute(code)
                result['analysis']['execution'] = exec_result
                
                if not exec_result['success'] and exec_result['stderr']:
                    error_analysis = ErrorAnalyzer.analyze_error(exec_result['stderr'], code)
                    result['analysis']['error_analysis'] = error_analysis
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'서버 오류: {str(e)}'
        }), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """
    통계 API
    
    Returns:
        {
            "success": bool,
            "statistics": {...}
        }
    """
    try:
        stats = db.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/validate', methods=['POST'])
def validate_only():
    """
    정적 분석만 수행 (실행 없이)
    """
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code:
            return jsonify({
                'success': False,
                'error': '코드가 비어있습니다'
            }), 400
        
        validation_result = CodeValidator.full_validation(code)
        
        return jsonify({
            'success': True,
            'validation': validation_result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🔍 Python Error Analyzer - Web Server")
    print("=" * 60)
    print(f"🌐 서버 주소: http://localhost:5000")
    print("=" * 60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
