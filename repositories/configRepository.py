import sqlite3
from typing import List, Dict, Any, Optional


class configRepository:
    def __init__(self, path: str):
        self.path = path

    def _get_connection(self):
        """Cria uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def update_value(self, key: str, value: str) -> bool:
        """
        Atualiza o valor da config identificada pela key.
        Retorna True se alguma linha foi atualizada, False caso contrário.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE config SET value = ? WHERE key = ?",
                    (value, key)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao atualizar config {key}: {e}")
            return False

    def get_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retorna um dicionário com a row correspondente a `key`, ou None se não existir.
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, context, key, value FROM config WHERE key = ? LIMIT 1",
                    (key,)
                )
                row = cursor.fetchone()
                conn.commit()  # mantém padrão do seu código (não estraga SELECT)
                if row:
                    return dict(row)
                return None
        except sqlite3.Error as e:
            print(f"Erro ao buscar config {key}: {e}")
            return None

    def get_all_by_context(self, context: str) -> List[Dict[str, Any]]:
        """
        Retorna todas as configs do context (ordenadas por key).
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, context, key, value FROM config WHERE context = ? ORDER BY key ASC",
                    (context,)
                )
                rows = cursor.fetchall()
                conn.commit()
                return [dict(r) for r in rows]
        except sqlite3.Error as e:
            print(f"Erro ao listar configs do contexto {context}: {e}")
            return []