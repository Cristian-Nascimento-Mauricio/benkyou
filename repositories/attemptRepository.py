import sqlite3
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime

class attemptRepository:
    def __init__(self, path: str):
        self.path = path
    
    def _get_connection(self):
        """Cria uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # CREATE - Criar uma nova tentativa
    def create_attempt(self, read: Optional[int], mean: int, card_id: int) -> Optional[Dict[str, Any]]:
        """
        Cria uma nova tentativa
        
        Args:
            read: 0, 1 ou None (NULL)
            mean: 0 ou 1 (não pode ser NULL)
            card_id: ID do card relacionado
            
        Returns:
            Dicionário com os dados da tentativa criada ou None em caso de erro
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if read is None:
                    cursor.execute(
                        "INSERT INTO attempt (read, mean, card_id) VALUES (NULL, ?, ?)",
                        (mean, card_id)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO attempt (read, mean, card_id) VALUES (?, ?, ?)",
                        (read, mean, card_id)
                    )
                
                conn.commit()
                return self.get_attempt_by_id(cursor.lastrowid)
                
        except sqlite3.IntegrityError as e:
            print(f"Erro ao criar tentativa: {e}")
            return None
        except sqlite3.Error as e:
            print(f"Erro de banco de dados: {e}")
            return None
    
    # READ - Buscar tentativa por ID
    def get_attempt_by_id(self, attempt_id: int) -> Optional[Dict[str, Any]]:
        """Busca uma tentativa pelo seu ID"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM attempt WHERE id = ?", (attempt_id,))
                attempt_data = cursor.fetchone()
                
                if not attempt_data:
                    return None
                
                return dict(attempt_data)
                
        except sqlite3.Error as e:
            print(f"Erro ao buscar tentativa: {e}")
            return None
    
    # READ - Buscar todas as tentativas de um card
    def get_attempts_by_card_id(self, card_id: int, limit: Optional[int] = None, 
                                order_by: str = "created_at DESC") -> List[Dict[str, Any]]:
        """
        Busca todas as tentativas de um card específico
        
        Args:
            card_id: ID do card
            limit: Número máximo de tentativas a retornar (opcional)
            order_by: Campo para ordenação (padrão: data decrescente)
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = f"SELECT * FROM attempt WHERE card_id = ? ORDER BY {order_by}"
                params = (card_id,)
                
                if limit:
                    query += " LIMIT ?"
                    params = (card_id, limit)
                
                cursor.execute(query, params)
                attempts = cursor.fetchall()
                
                return [dict(attempt) for attempt in attempts]
                
        except sqlite3.Error as e:
            print(f"Erro ao buscar tentativas do card: {e}")
            return []
    
    # READ - Buscar todas as tentativas
    def get_all_attempts(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Busca todas as tentativas do banco"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM attempt ORDER BY created_at DESC"
                if limit:
                    query += " LIMIT ?"
                    cursor.execute(query, (limit,))
                else:
                    cursor.execute(query)
                
                attempts = cursor.fetchall()
                return [dict(attempt) for attempt in attempts]
                
        except sqlite3.Error as e:
            print(f"Erro ao buscar todas as tentativas: {e}")
            return []
    
    # UPDATE - Atualizar uma tentativa existente
    def update_attempt(self, attempt_id: int, read: Optional[int] = None, 
                      mean: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Atualiza os dados de uma tentativa"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                update_fields = []
                params = []
                
                if read is not None:
                    if read is None:
                        update_fields.append("read = NULL")
                    else:
                        update_fields.append("read = ?")
                        params.append(read)
                
                if mean is not None:
                    update_fields.append("mean = ?")
                    params.append(mean)
                
                if not update_fields:
                    return self.get_attempt_by_id(attempt_id)
                
                params.append(attempt_id)
                query = f"UPDATE attempt SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, params)
                
                conn.commit()
                return self.get_attempt_by_id(attempt_id)
                
        except sqlite3.Error as e:
            print(f"Erro ao atualizar tentativa: {e}")
            return None
    
    # DELETE - Remover uma tentativa
    def delete_attempt(self, attempt_id: int) -> bool:
        """Remove uma tentativa pelo ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM attempt WHERE id = ?", (attempt_id,))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"Erro ao deletar tentativa: {e}")
            return False
    
    # DELETE - Remover todas as tentativas de um card
    def delete_attempts_by_card_id(self, card_id: int) -> int:
        """Remove todas as tentativas de um card específico"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM attempt WHERE card_id = ?", (card_id,))
                conn.commit()
                
                return cursor.rowcount
                
        except sqlite3.Error as e:
            print(f"Erro ao deletar tentativas do card: {e}")
            return 0
    
    # Métodos de análise estatística
    
    def get_card_performance(self, card_id: int) -> Dict[str, Any]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total de tentativas
                cursor.execute(
                    "SELECT COUNT(*) FROM attempt WHERE card_id = ?",
                    (card_id,)
                )
                total_attempts = cursor.fetchone()[0]
                
                if total_attempts == 0:
                    return {
                        'card_id': card_id,
                        'total_attempts': 0,
                        'read_correct': 0,
                        'read_incorrect': 0,
                        'read_null': 0,
                        'mean_correct': 0,
                        'mean_incorrect': 0,
                        'accuracy': 0.0
                    }
                
                # Leituras
                cursor.execute(
                    """SELECT 
                        SUM(CASE WHEN read = 1 THEN 1 ELSE 0 END) as read_correct,
                        SUM(CASE WHEN read = 0 THEN 1 ELSE 0 END) as read_incorrect,
                        SUM(CASE WHEN read IS NULL THEN 1 ELSE 0 END) as read_null
                    FROM attempt WHERE card_id = ?""",
                    (card_id,)
                )
                read_stats = cursor.fetchone()
                
                # Significados
                cursor.execute(
                    """SELECT 
                        SUM(CASE WHEN mean = 1 THEN 1 ELSE 0 END) as mean_correct,
                        SUM(CASE WHEN mean = 0 THEN 1 ELSE 0 END) as mean_incorrect
                    FROM attempt WHERE card_id = ?""",
                    (card_id,)
                )
                mean_stats = cursor.fetchone()
                
                # Calcula acurácia (considerando read=NULL como mean)
                cursor.execute(
                    """SELECT 
                        AVG(
                            (COALESCE(read, mean) + mean) / 2.0
                        ) * 100 as accuracy
                    FROM attempt WHERE card_id = ?""",
                    (card_id,)
                )
                accuracy_result = cursor.fetchone()
                accuracy = round(accuracy_result[0] or 0, 2) if accuracy_result[0] is not None else 0.0
                
                return {
                    'card_id': card_id,
                    'total_attempts': total_attempts,
                    'read_correct': read_stats[0] or 0,
                    'read_incorrect': read_stats[1] or 0,
                    'read_null': read_stats[2] or 0,
                    'mean_correct': mean_stats[0] or 0,
                    'mean_incorrect': mean_stats[1] or 0,
                    'accuracy': accuracy
                }
                
        except sqlite3.Error as e:
            print(f"Erro ao calcular desempenho do card: {e}")
            return {}
    
    def get_overall_performance(self) -> Dict[str, Any]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Totais
                cursor.execute("SELECT COUNT(*) FROM attempt")
                total_attempts = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT card_id) FROM attempt")
                cards_with_attempts = cursor.fetchone()[0]
                
                if total_attempts == 0:
                    return {
                        'total_attempts': 0,
                        'cards_with_attempts': 0,
                        'average_accuracy': 0.0,
                        'daily_attempts': []
                    }
                
                # Acurácia geral
                cursor.execute(
                    """SELECT 
                        AVG(
                            (COALESCE(read, mean) + mean) / 2.0
                        ) * 100 as overall_accuracy
                    FROM attempt"""
                )
                accuracy_result = cursor.fetchone()
                overall_accuracy = round(accuracy_result[0] or 0, 2) if accuracy_result[0] is not None else 0.0
                
                # Tentativas por dia
                cursor.execute(
                    """SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as attempts,
                        AVG((COALESCE(read, mean) + mean) / 2.0) * 100 as daily_accuracy
                    FROM attempt 
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                    LIMIT 30"""
                )
                daily_attempts = []
                for row in cursor.fetchall():
                    daily_attempts.append({
                        'date': row[0],
                        'attempts': row[1],
                        'accuracy': round(row[2] or 0, 2)
                    })
                
                return {
                    'total_attempts': total_attempts,
                    'cards_with_attempts': cards_with_attempts,
                    'average_accuracy': overall_accuracy,
                    'daily_attempts': daily_attempts
                }
                
        except sqlite3.Error as e:
            print(f"Erro ao calcular desempenho geral: {e}")
            return {}
    
    def get_recent_attempts(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    """SELECT 
                        a.*,
                        c.word,
                        c.category
                    FROM attempt a
                    JOIN card c ON a.card_id = c.id
                    ORDER BY a.created_at DESC
                    LIMIT ?""",
                    (limit,)
                )
                
                attempts = cursor.fetchall()
                return [dict(attempt) for attempt in attempts]
                
        except sqlite3.Error as e:
            print(f"Erro ao buscar tentativas recentes: {e}")
            return []
    
    def get_attempts_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    """SELECT 
                        a.*,
                        c.word,
                        c.category
                    FROM attempt a
                    JOIN card c ON a.card_id = c.id
                    WHERE DATE(a.created_at) BETWEEN ? AND ?
                    ORDER BY a.created_at DESC""",
                    (start_date, end_date)
                )
                
                attempts = cursor.fetchall()
                return [dict(attempt) for attempt in attempts]
                
        except sqlite3.Error as e:
            print(f"Erro ao buscar tentativas por data: {e}")
            return []

    def get_date_today(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT date('now')")
                today = cursor.fetchone()[0]
                return today

        except sqlite3.Error as e:
            print(f"Erro ao pegar data de hoje: {e}")
            return None
        
    def get_activity_statistics(self, days: int) -> List[Dict[str, Any]]:
        days_map = {
            7:  "-6 days",
            15: "-14 days",
            30: "-29 days"
        }

        interval = days_map.get(days)
        if not interval:
            raise ValueError("days must be 7, 15 or 30")

        sql = """
            SELECT
                date(created_at) AS day,
                COALESCE(SUM(read), mean)  AS read,
                COALESCE(SUM(mean), 0)  AS mean,
                COUNT(attempt.id)       AS attempt
            FROM attempt
            WHERE date(created_at) >= date('now', ?)
            GROUP BY day
            ORDER BY day ASC;
        """

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (interval,))
                rows = cursor.fetchall()

                conn.commit()  # mantém o padrão do seu código
        
                return [
                    {
                        "day": row[0],
                        "read": row[1],
                        "mean": row[2],
                        "attempt": row[3]
                    }
                    for row in rows
                ]

        except sqlite3.Error as e:
            print(f"Erro ao buscar estatísticas: {e}")
            return []

    def get_already_learned_cards(self, threshold: float = 0.83) -> List[int]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT date('now')")
                today = cursor.fetchone()[0]
                return today

        except sqlite3.Error as e:
            print(f"Erro ao pegar cards: {e}")
            return None
        
    def create_bulk_attempts(self, attempts_data: List[Tuple[Optional[int], int, int]]) -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                created_count = 0
                for read, mean, card_id in attempts_data:
                    if read is None:
                        cursor.execute(
                            "INSERT INTO attempt (read, mean, card_id) VALUES (NULL, ?, ?)",
                            (mean, card_id)
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO attempt (read, mean, card_id) VALUES (?, ?, ?)",
                            (read, mean, card_id)
                        )
                    created_count += 1
                
                conn.commit()
                return created_count
                
        except sqlite3.Error as e:
            print(f"Erro ao criar tentativas em massa: {e}")
            return 0