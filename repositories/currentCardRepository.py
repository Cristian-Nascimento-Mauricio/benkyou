import sqlite3

class currentCardRepository:
    def __init__(self, db_path: str = "cards.db"):
        self.path = db_path
    
    def _get_connection(self):
        """Cria uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def get_randon_card_in_currentCard(self,lastID:int = -1):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT card_id FROM currentCard WHERE card_id != ? ORDER BY RANDOM() LIMIT 1;",[lastID])

                id = cursor.fetchone()[0]
            
                return id
            
        except sqlite3.Error as e:
            print(f"Erro ao pegar a id: {e}")
            return False
        
    def select_first_three_static(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                        SELECT 
                            cc.card_id,
                            AVG(score) as average,
                            COUNT(*) as count
                        FROM currentCard cc
                        INNER JOIN (
                            SELECT 
                                card_id,
                                (COALESCE(read, mean) + mean) / 2.0 as score,
                                created_at,
                                ROW_NUMBER() OVER (PARTITION BY card_id ORDER BY created_at DESC) as rn
                            FROM attempt
                        ) last_attempts ON cc.card_id = last_attempts.card_id 
                            AND last_attempts.rn <= 3
                        WHERE cc.created_at < last_attempts.created_at
                        GROUP BY cc.card_id
                        ORDER BY average ASC;
                ''')

                rows = cursor.fetchall()
                stats = []
                
                for row in rows:
                    stat = {
                        'card_id': row[0],
                        'average': row[1],
                        'count': row[2]
                    }
                    stats.append(stat)

                return stats
            
        except sqlite3.Error as e:
            print(f"Erro ao pegar a quantidade: {e}")
            return False

    def len_current(self):
        """Retorna a quantidade de registros na tabela currentCard"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM currentCard")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Erro ao pegar a quantidade: {e}")
            return False

    def get_already_learned(self,cardId):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT
                        card_id,
                        COUNT(*) AS count,
                        AVG(
                            (COALESCE(read,0) + COALESCE(mean,0)) / 2.0
                        ) AS porcent
                    FROM (
                    SELECT *
                    FROM attempt
                    WHERE card_id = ?
                    ORDER BY created_at DESC
                    LIMIT 10
                    );

                ''',(cardId,))

                row = cursor.fetchone()

                if row is None:
                    return None

                card = {
                    "id": row[0],
                    "count": row[1],
                    "porcent": row[2]
                }
                return card
        except sqlite3.Error as e:
            print(f"Erro ao pegar a quantidade: {e}")
            return False 


    def create(self, card_id: int):
        """Cria um novo registro em currentCard"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO currentCard (card_id) VALUES (?)", 
                    (card_id,)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao criar: {e}")
            return None
    
    def read_all(self):
        """Retorna todos os registros de currentCard"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM currentCard ORDER BY created_at DESC")
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao ler todos: {e}")
            return []
    
    def read_by_id(self, id: int):
        """Retorna um registro específico pelo ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM currentCard WHERE id = ?", (id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erro ao ler por ID: {e}")
            return None
    
    def update(self, id: int, card_id: int):
        """Atualiza um registro existente"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE currentCard SET card_id = ? WHERE id = ?", 
                    (card_id, id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao atualizar: {e}")
            return False
    
    def delete(self, id: int):
        """Remove um registro pelo ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM currentCard WHERE card_id = ?", (id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao deletar: {e}")
            return False
    
    def get_last(self):
        """Retorna o último registro inserido"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM currentCard ORDER BY created_at DESC LIMIT 1"
                )
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erro ao pegar último: {e}")
            return None
    
    def get_by_card_id(self, card_id: int):
        """Retorna registros por card_id"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM currentCard WHERE card_id = ? ORDER BY created_at DESC",
                    (card_id,)
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar por card_id: {e}")
            return []
    
    def delete_all(self):
        """Remove todos os registros da tabela"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM currentCard")
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Erro ao deletar tudo: {e}")
            return 0
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM currentCard WHERE id = ?", (id,))
        self.conn.commit()
        return cursor.rowcount