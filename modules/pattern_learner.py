"""
패턴 학습 모듈 - 에러 패턴 분석 및 통계
"""

from typing import Dict, List, Any
from .error_database import ErrorDatabase


class PatternLearner:
    """에러 패턴 학습 및 통계"""
    
    @staticmethod
    def get_error_statistics(db: ErrorDatabase, limit: int = 10) -> Dict[str, Any]:
        """
        에러 통계 조회
        
        Args:
            db: ErrorDatabase 인스턴스
            limit: 상위 N개 조회
        
        Returns:
            통계 딕셔너리
        """
        import sqlite3
        
        stats = {
            'total_errors': 0,
            'error_types': {},
            'common_patterns': [],
            'recent_errors': []
        }
        
        # DB 연결
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        try:
            # 총 에러 개수
            cursor.execute("SELECT COUNT(*) FROM error_history")
            stats['total_errors'] = cursor.fetchone()[0]
            
            # 에러 타입별 통계
            cursor.execute("""
                SELECT error_type, COUNT(*) as count
                FROM error_history
                GROUP BY error_type
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))
            
            for row in cursor.fetchall():
                error_type, count = row
                stats['error_types'][error_type] = count
            
            # 자주 발생하는 패턴 (에러 메시지 기준)
            cursor.execute("""
                SELECT error_type, error_message, COUNT(*) as count
                FROM error_history
                GROUP BY error_type, error_message
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))
            
            for row in cursor.fetchall():
                error_type, error_message, count = row
                stats['common_patterns'].append({
                    'error_type': error_type,
                    'error_message': error_message,
                    'count': count
                })
            
            # 최근 에러
            cursor.execute("""
                SELECT error_type, error_message, created_at
                FROM error_history
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            for row in cursor.fetchall():
                error_type, error_message, created_at = row
                stats['recent_errors'].append({
                    'error_type': error_type,
                    'error_message': error_message,
                    'timestamp': created_at
                })
        finally:
            conn.close()
        
        return stats
    
    @staticmethod
    def get_common_patterns(db: ErrorDatabase, limit: int = 10) -> List[Dict[str, Any]]:
        """
        자주 발생하는 에러 패턴 반환
        
        Args:
            db: ErrorDatabase 인스턴스
            limit: 상위 N개
        
        Returns:
            패턴 리스트
        """
        import sqlite3
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT error_type, error_message, COUNT(*) as count
                FROM error_history
                GROUP BY error_type, error_message
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))
            
            patterns = []
            for row in cursor.fetchall():
                error_type, error_message, count = row
                patterns.append({
                    'error_type': error_type,
                    'error_message': error_message,
                    'count': count
                })
        finally:
            conn.close()
        
        return patterns
