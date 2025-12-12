"""
모듈 5: 에러 데이터베이스
에러 히스토리 저장, 검색, 학습
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import os


class ErrorDatabase:
    """에러 히스토리 데이터베이스"""
    
    def __init__(self, db_path: str = 'data/error_history.db'):
        """
        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 데이터베이스 초기화
        self._init_database()
    
    def _init_database(self):
        """데이터베이스 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 에러 히스토리 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_hash TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT,
                line_number INTEGER,
                code_snippet TEXT,
                full_stderr TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 해결책 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_id INTEGER NOT NULL,
                solution_text TEXT NOT NULL,
                solution_type TEXT,
                applied BOOLEAN DEFAULT 0,
                success BOOLEAN DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (error_id) REFERENCES error_history(id)
            )
        ''')
        
        # 에러 패턴 테이블 (자주 발생하는 패턴)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                pattern TEXT NOT NULL,
                occurrence_count INTEGER DEFAULT 1,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(error_type, pattern)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def _hash_code(code: str) -> str:
        """코드의 해시값 생성"""
        return hashlib.md5(code.encode()).hexdigest()
    
    def save_error(self, code: str, error_analysis: Dict) -> int:
        """
        에러 저장
        
        Args:
            code: 에러가 발생한 코드
            error_analysis: ErrorAnalyzer.analyze_error() 결과
            
        Returns:
            error_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        code_hash = self._hash_code(code)
        
        cursor.execute('''
            INSERT INTO error_history 
            (code_hash, error_type, error_message, line_number, code_snippet, full_stderr)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            code_hash,
            error_analysis.get('error_type', 'Unknown'),
            error_analysis.get('error_message', ''),
            error_analysis.get('line_number'),
            code[:500],  # 처음 500자만
            error_analysis.get('raw_error', '')
        ))
        
        error_id = cursor.lastrowid
        
        # 해결책 저장
        if 'solutions' in error_analysis:
            for solution in error_analysis['solutions']:
                cursor.execute('''
                    INSERT INTO solutions (error_id, solution_text, solution_type)
                    VALUES (?, ?, ?)
                ''', (error_id, solution, 'auto_generated'))
        
        # 패턴 업데이트
        error_type = error_analysis.get('error_type', 'Unknown')
        pattern = error_analysis.get('error_message', '')[:200]
        
        cursor.execute('''
            INSERT INTO error_patterns (error_type, pattern, occurrence_count)
            VALUES (?, ?, 1)
            ON CONFLICT(error_type, pattern) 
            DO UPDATE SET 
                occurrence_count = occurrence_count + 1,
                last_seen = CURRENT_TIMESTAMP
        ''', (error_type, pattern))
        
        conn.commit()
        conn.close()
        
        return error_id
    
    def find_similar_errors(self, error_analysis: Dict, limit: int = 5) -> List[Dict]:
        """
        유사한 에러 검색
        
        Args:
            error_analysis: 현재 에러 분석 결과
            limit: 최대 결과 수
            
        Returns:
            유사 에러 리스트
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        error_type = error_analysis.get('error_type', 'Unknown')
        
        # 같은 에러 타입 검색
        cursor.execute('''
            SELECT 
                eh.*,
                GROUP_CONCAT(s.solution_text, '|||') as solutions,
                GROUP_CONCAT(s.success, ',') as success_flags
            FROM error_history eh
            LEFT JOIN solutions s ON eh.id = s.error_id
            WHERE eh.error_type = ?
            GROUP BY eh.id
            ORDER BY eh.created_at DESC
            LIMIT ?
        ''', (error_type, limit))
        
        results = []
        for row in cursor.fetchall():
            solutions = row['solutions'].split('|||') if row['solutions'] else []
            success_flags = row['success_flags'].split(',') if row['success_flags'] else []
            
            results.append({
                'id': row['id'],
                'error_type': row['error_type'],
                'error_message': row['error_message'],
                'line_number': row['line_number'],
                'code_snippet': row['code_snippet'],
                'solutions': solutions,
                'created_at': row['created_at']
            })
        
        conn.close()
        return results
    
    def mark_solution_result(self, solution_id: int, success: bool):
        """
        해결책 적용 결과 기록
        
        Args:
            solution_id: 해결책 ID
            success: 성공 여부
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE solutions
            SET applied = 1, success = ?
            WHERE id = ?
        ''', (1 if success else 0, solution_id))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        """
        통계 정보 조회
        
        Returns:
            {
                'total_errors': int,
                'error_by_type': {...},
                'most_common_patterns': [...]
            }
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 전체 에러 개수
        cursor.execute('SELECT COUNT(*) as count FROM error_history')
        total_errors = cursor.fetchone()['count']
        
        # 타입별 에러 개수
        cursor.execute('''
            SELECT error_type, COUNT(*) as count
            FROM error_history
            GROUP BY error_type
            ORDER BY count DESC
        ''')
        error_by_type = {row['error_type']: row['count'] for row in cursor.fetchall()}
        
        # 가장 흔한 패턴
        cursor.execute('''
            SELECT error_type, pattern, occurrence_count
            FROM error_patterns
            ORDER BY occurrence_count DESC
            LIMIT 10
        ''')
        most_common_patterns = [
            {
                'error_type': row['error_type'],
                'pattern': row['pattern'],
                'count': row['occurrence_count']
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            'total_errors': total_errors,
            'error_by_type': error_by_type,
            'most_common_patterns': most_common_patterns
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """최근 에러 조회"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM error_history
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results


# 테스트
if __name__ == '__main__':
    print("=" * 60)
    print("🗄️  에러 데이터베이스 테스트")
    print("=" * 60)
    
    # DB 초기화
    db = ErrorDatabase('data/error_history.db')
    
    # 테스트 에러 저장
    test_error = {
        'error_type': 'ModuleNotFoundError',
        'error_message': "No module named 'numpy'",
        'line_number': 1,
        'raw_error': "Traceback...",
        'solutions': ['pip install numpy', '철자 확인']
    }
    
    error_id = db.save_error("import numpy", test_error)
    print(f"✅ 에러 저장됨 (ID: {error_id})")
    
    # 유사 에러 검색
    similar = db.find_similar_errors(test_error)
    print(f"\n🔍 유사 에러 {len(similar)}개 발견")
    
    # 통계
    stats = db.get_statistics()
    print(f"\n📊 통계:")
    print(f"   - 총 에러: {stats['total_errors']}개")
    print(f"   - 타입별: {stats['error_by_type']}")
    
    print("\n" + "=" * 60)
