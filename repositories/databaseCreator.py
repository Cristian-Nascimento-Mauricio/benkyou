import sqlite3
from pathlib import Path

class databaseCreator:  # Convenção: CamelCase para nomes de classe
    def __init__(self, db_name='../db/database.db'):
        current_file = Path(__file__).resolve()
        current_dir = current_file.parent
        self.db_path = (current_dir / db_name).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"📍 Script em: {current_dir}")
        print(f"🗄️  Banco em: {self.db_path}")
    
    def create_database(self):
        """Cria o banco de dados com todas as tabelas"""
        try:
            print(f"🔧 Criando banco em: {self.db_path}")
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 1. Tabela CARD (corrigido)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "card" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "word" TEXT NOT NULL UNIQUE,           
                    "category" TEXT NOT NULL,      
                    "created_at" TEXT DEFAULT CURRENT_TIMESTAMP,
                    "updated_at" TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 2. Tabela MEANING (adicionado AUTOINCREMENT)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "meaning" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT, 
                    "mean" TEXT NOT NULL,
                    "card_id" INTEGER NOT NULL,
                    FOREIGN KEY("card_id") REFERENCES "card"("id") 
                    ON DELETE CASCADE
                )
            ''')
            
            # 3. Tabela READING
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "reading" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "read" TEXT NOT NULL,
                    "card_id" INTEGER NOT NULL,
                    FOREIGN KEY("card_id") REFERENCES "card"("id") 
                    ON DELETE CASCADE
                )
            ''')
            
            # 4. Tabela ATTEMPT (corrigida a PK)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "attempt" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,  
                    "read" INTEGER CHECK("read" IN (0, 1)),
                    "mean" INTEGER NOT NULL CHECK("mean" IN (0, 1)),
                    "card_id" INTEGER NOT NULL,
                    "created_at" TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY("card_id") REFERENCES "card"("id") 
                    ON DELETE CASCADE,
                    UNIQUE("id", "card_id")  
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "currentCard" (
                    "id"	INTEGER PRIMARY KEY AUTOINCREMENT,
                    "card_id"	INTEGER NOT NULL,
                    "created_at"	TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY("card_id") REFERENCES "card"("id") ON DELETE CASCADE
                );
            ''')       

            cursor.execute('''CREATE TABLE IF NOT EXISTS "config" (
                "id"	INTEGER NOT NULL UNIQUE,
                "context"	TEXT NOT NULL,
                "key"	TEXT NOT NULL UNIQUE,
                "value"	TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)

            );''')

            #Default config
            cursor.execute('''INSERT OR IGNORE INTO "config" ( context, key, value) VALUES ( 'levels', 'N5', 'ON')''')
            cursor.execute('''INSERT OR IGNORE INTO "config" ( context, key, value) VALUES ( 'levels', 'N4', 'OFF')''')
            cursor.execute('''INSERT OR IGNORE INTO "config" ( context, key, value) VALUES ( 'levels', 'N3', 'OFF')''')
            cursor.execute('''INSERT OR IGNORE INTO "config" ( context, key, value) VALUES ( 'levels', 'N2', 'OFF')''')
            cursor.execute('''INSERT OR IGNORE INTO "config" ( context, key, value) VALUES ( 'levels', 'N1', 'OFF')''')
            cursor.execute('''INSERT OR IGNORE INTO "config" ( context, key, value) VALUES ( 'select-card', 'range-select-card', '0.75')''')

            conn.commit()
            conn.close()
            
            print("✅ Banco criado com sucesso!")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Erro SQLite: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro geral: {type(e).__name__}: {e}")
            return False
    
    def get_db_info(self):
        """Retorna informações sobre o banco"""
        return {
            'path': str(self.db_path),
            'parent': str(self.db_path.parent),
            'exists': self.db_path.exists(),
            'parent_exists': self.db_path.parent.exists()
        }


# Teste rápido
if __name__ == "__main__":
    creator = DatabaseCreator()
    if creator.create_database():
        print("🎉 Tudo funcionando!")
    else:
        print("⚠️ Problemas encontrados.")