import sqlite3
from typing import List, Dict, Optional, Any

class cardRepository:
    def __init__(self, path: str):
        self.path = path
    
    def _get_connection(self):
        """Cria uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # CREATE - Criar um novo card
    def create_card(self, word: str, category: str, 
                   readings: List[str], meanings: List[str]) -> Optional[Dict[str, Any]]:
        """Cria um novo card com readings e meanings"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Inserir o card
                cursor.execute(
                    "INSERT INTO card (word, category) VALUES (?, ?)",
                    (word, category)
                )
                card_id = cursor.lastrowid
                
                # Inserir readings
                for reading in readings:
                    cursor.execute(
                        "INSERT INTO reading (read, card_id) VALUES (?, ?)",
                        (reading, card_id)
                    )
                
                # Inserir meanings
                for meaning in meanings:
                    cursor.execute(
                        "INSERT INTO meaning (mean, card_id) VALUES (?, ?)",
                        (meaning, card_id)
                    )
                
                conn.commit()
                return self.get_card_by_id(card_id)
                
        except sqlite3.IntegrityError as e:
            print(f"Erro ao criar card: {e}")
            return None
    
    def create_reading(self,cardId,read):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO reading (read, card_id) VALUES (?, ?)",
                    (read, cardId) 
                )                
                conn.commit()
                return self.get_card_by_id(cursor.lastrowid)
                
        except sqlite3.IntegrityError as e:
            print(f"Erro ao criar reading: {e}")
            return None       
    
    def create_meaning(self,cardId,mean):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO meaning (mean, card_id) VALUES (?, ?)",
                    (mean, cardId)  
                )                
                conn.commit()
                return self.get_card_by_id(cursor.lastrowid)
                
        except sqlite3.IntegrityError as e:
            print(f"Erro ao criar meaning: {e}")
            return None      

    def card_stastic_all(self):
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                rows = cursor.execute("""SELECT 
                                    card.id, 
                                    card.word, 
                                    card.category,
                                    t.c_attempt  AS c_attempt,
                                    t.c_read AS c_read,
                                    t.c_mean AS c_mean
                                FROM card
                                LEFT JOIN (
                                    SELECT 
                                        attempt.card_id,
                                        COUNT(attempt.id) AS c_attempt,
                                        SUM(attempt.read) AS c_read,
                                        SUM(attempt.mean) AS c_mean
                                    FROM attempt
                                    GROUP BY attempt.card_id
                                ) t ON t.card_id = card.id
                                ORDER BY c_attempt DESC;"""
                )

                list = []
                for row in rows:
                    list.append({
                        "id":row["id"],
                        "word":row["word"],
                        "category":row["category"],
                        "countRead":row["c_read"],
                        "countMean":row["c_mean"],
                        "countAttempt":row["c_attempt"]
                    })
                return list
                
        except sqlite3.Error as e:
            print(f"Errro ao buscar estaticas: {e}")
            return None

    # READ - Buscar card por ID com readings e meanings
    def get_card_by_id(self, card_id: int) -> Optional[Dict[str, Any]]:
        """Busca um card pelo ID com todas as readings e meanings"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Buscar o card
                cursor.execute("SELECT * FROM card WHERE id = ?", (card_id,))
                card_data = cursor.fetchone()
                
                if not card_data:
                    return None
                
                # Converter card para dicionário
                card = dict(card_data)
                
                # Buscar readings
                cursor.execute("SELECT read FROM reading WHERE card_id = ?", (card_id,))
                reading = cursor.fetchall()
                card['reading'] = [row[0] for row in reading]
                
                # Buscar meanings
                cursor.execute("SELECT mean FROM meaning WHERE card_id = ?", (card_id,))
                meaning = cursor.fetchall()
                card['meaning'] = [row[0] for row in meaning]
                
                return card
                
        except sqlite3.Error as e:
            print(f"Erro ao buscar card: {e}")
            return None
    
    # READ - Buscar todos os cards com readings e meanings
    def get_all_cards(self) -> List[Dict[str, Any]]:
        """Busca todos os cards com suas readings e meanings"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Buscar todos os cards
                cursor.execute("SELECT * FROM card ORDER BY id")
                all_cards = cursor.fetchall()
                
                cards_with_details = []
                for card_row in all_cards:
                    card = dict(card_row)
                    card_id = card['id']
                    
                    # Buscar readings para este card
                    cursor.execute("SELECT id, read FROM reading WHERE card_id = ?", (card_id,))
                    card['reading'] = [row[1] for row in cursor.fetchall()]
                    
                    # Buscar meanings para este card
                    cursor.execute("SELECT id, mean FROM meaning WHERE card_id = ?", (card_id,))
                    card['meaning'] = [row[1] for row in cursor.fetchall()]
                    
                    cards_with_details.append(card)
                
                return cards_with_details
                
        except sqlite3.Error as e:
            print(f"Erro ao buscar todos os cards: {e}")
            return []
    
    # READ - Buscar cards por palavra
    def get_cards_by_word(self, word: str) -> List[Dict[str, Any]]:
        """Busca cards por palavra (busca parcial)"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Buscar cards pela palavra
                cursor.execute(
                    "SELECT * FROM card WHERE word LIKE ? ORDER BY id",
                    (f"%{word}%",)
                )
                cards = cursor.fetchall()
                
                cards_with_details = []
                for card_row in cards:
                    card = dict(card_row)
                    card_id = card['id']
                    
                    # Buscar readings
                    cursor.execute("SELECT id, read FROM reading WHERE card_id = ?", (card_id,))
                    readings = cursor.fetchall()
                    card['readings'] = [dict(row) for row in readings]
                    
                    # Buscar meanings
                    cursor.execute("SELECT id, mean FROM meaning WHERE card_id = ?", (card_id,))
                    meanings = cursor.fetchall()
                    card['meanings'] = [dict(row) for row in meanings]
                    
                    cards_with_details.append(card)
                
                return cards_with_details
                
        except sqlite3.Error as e:
            print(f"Erro ao buscar cards por palavra: {e}")
            return []
    
    # UPDATE - Atualizar um card existente
    def update_card(self, card_id: int, word: str = None, category: str = None,
                   readings: List[str] = None, meanings: List[str] = None) -> Optional[Dict[str, Any]]:
        """Atualiza um card existente"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Atualizar dados básicos do card se fornecidos
                if word or category:
                    update_fields = []
                    params = []
                    
                    if word:
                        update_fields.append("word = ?")
                        params.append(word)
                    
                    if category:
                        update_fields.append("category = ?")
                        params.append(category)
                    
                    # Adicionar updated_at
                    update_fields.append("updated_at = CURRENT_TIMESTAMP")
                    
                    params.append(card_id)
                    query = f"UPDATE card SET {', '.join(update_fields)} WHERE id = ?"
                    cursor.execute(query, params)
                
                # Atualizar readings se fornecidas
                if readings is not None:
                    # Remover readings antigas
                    cursor.execute("DELETE FROM reading WHERE card_id = ?", (card_id,))
                    
                    # Inserir novas readings
                    for reading in readings:
                        cursor.execute(
                            "INSERT INTO reading (read, card_id) VALUES (?, ?)",
                            (reading, card_id)
                        )
                
                # Atualizar meanings se fornecidas
                if meanings is not None:
                    # Remover meanings antigas
                    cursor.execute("DELETE FROM meaning WHERE card_id = ?", (card_id,))
                    
                    # Inserir novas meanings
                    for meaning in meanings:
                        cursor.execute(
                            "INSERT INTO meaning (mean, card_id) VALUES (?, ?)",
                            (meaning, card_id)
                        )
                
                conn.commit()
                return self.get_card_by_id(card_id)
                
        except sqlite3.Error as e:
            print(f"Erro ao atualizar card: {e}")
            return None
    
    # DELETE - Remover um card
    def delete_card(self, card_id: int) -> bool:
        """Remove um card pelo ID (cascade remove readings e meanings)"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar se o card existe
                cursor.execute("SELECT id FROM card WHERE id = ?", (card_id,))
                if not cursor.fetchone():
                    return False
                
                # Deletar o card (cascade irá remover readings e meanings automaticamente)
                cursor.execute("DELETE FROM card WHERE id = ?", (card_id,))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"Erro ao deletar card: {e}")
            return False

    def get_cards_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Busca cards por categoria"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Buscar cards pela categoria
                cursor.execute(
                    "SELECT * FROM card WHERE category = ? ORDER BY id",
                    (category,)
                )
                cards = cursor.fetchall()
                
                cards_with_details = []
                for card_row in cards:
                    card = dict(card_row)
                    card_id = card['id']
                    
                    # Buscar readings
                    cursor.execute("SELECT id, read FROM reading WHERE card_id = ?", (card_id,))
                    readings = cursor.fetchall()
                    card["reading"] = [row["read"] for row in readings]
                    
                    # Buscar meanings
                    cursor.execute("SELECT id, mean FROM meaning WHERE card_id = ?", (card_id,))
                    meanings = cursor.fetchall()
                    card["meaning"] = [row["mean"] for row in meanings]
                    
                    cards_with_details.append(card)
                
                return cards_with_details
                
        except sqlite3.Error as e:
            print(f"Erro ao buscar cards por categoria: {e}")
            return []

    def selectCards(self,amount: int = 1, category: Optional[str] = [], range:float = 0.75 ) -> List[int]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                paramCategory = ",".join("?" for _ in category)

                sql = f'''
                    SELECT id
                    FROM (
                        SELECT card.*,
                        (
                            SELECT
                                (SUM(COALESCE(recent.read, recent.mean)) + SUM(recent.mean))
                                / NULLIF(COUNT(recent.id) * 2.0, 0.0)
                            FROM (
                                SELECT *
                                FROM attempt
                                WHERE card.id = attempt.card_id
                                ORDER BY attempt.created_at DESC
                                LIMIT 10
                            ) AS recent
                        ) AS n
                        FROM card
                        WHERE id NOT IN (
                            SELECT card_id FROM currentCard
                        )
                        AND card.category IN ({paramCategory})
                    )
                    WHERE COALESCE( n , 0.0) < ?
                    ORDER BY RANDOM() * (COALESCE( n , 0.01) * COALESCE( n , 0.01))
                    ASC
                    LIMIT ?;
                '''

                params = [*category, range, amount]

                cursor.execute(sql, params)
                rows = cursor.fetchall()

                return [row[0] for row in rows]
                
        except sqlite3.Error as e:
            print(f"Erro ao selecionar cards: {e}")
            return False
        
    def get_readings_by_card_id(self, card_id: int) -> List[Dict[str, Any]]:
        """Busca todas as readings de um card específico"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT id, read FROM reading WHERE card_id = ? ORDER BY id",
                    (card_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            print(f"Erro ao buscar readings: {e}")
            return []
    
    def get_meanings_by_card_id(self, card_id: int) -> List[Dict[str, Any]]:
        """Busca todos os meanings de um card específico"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT id, mean FROM meaning WHERE card_id = ? ORDER BY id",
                    (card_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            print(f"Erro ao buscar meanings: {e}")
            return []
        """Retorna estatísticas gerais do banco"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total de cards
                cursor.execute('SELECT COUNT(*) as count FROM card')
                stats['total_cards'] = cursor.fetchone()['count']
                
                # Cards por categoria
                cursor.execute('''
                    SELECT category, COUNT(*) as count 
                    FROM card 
                    GROUP BY category 
                    ORDER BY count DESC
                ''')
                stats['by_category'] = [dict(row) for row in cursor.fetchall()]
                
                # Total de tentativas
                cursor.execute('SELECT COUNT(*) as count FROM attempt')
                stats['total_attempts'] = cursor.fetchone()['count']
                
                # Taxa de acerto geral
                cursor.execute('''
                    SELECT 
                        AVG(read) * 100 as reading_accuracy,
                        AVG(mean) * 100 as meaning_accuracy
                    FROM attempt
                ''')
                accuracy = cursor.fetchone()
                stats['reading_accuracy'] = round(accuracy['reading_accuracy'] or 0, 2)
                stats['meaning_accuracy'] = round(accuracy['meaning_accuracy'] or 0, 2)
                
                return stats
                
        except Exception as e:
            print(f"❌ Erro ao calcular estatísticas: {e}")
            return {}