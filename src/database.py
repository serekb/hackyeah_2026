import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Wczytanie zmiennych z pliku .env
load_dotenv()

# Pobranie bezpiecznego linku z .env
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """
    Funkcja nawiązująca połączenie z bazą Neon.
    Zwraca obiekt połączenia lub None w przypadku błędu.
    """
    if not DATABASE_URL:
        print("❌ Błąd: Brak DATABASE_URL. Czy plik .env istnieje?")
        return None

    try:
        # cursor_factory=RealDictCursor sprawia, że wyniki to słowniki (np. wiersz['imie'])
        conn = psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        print(f"❌ Błąd połączenia z bazą danych: {e}")
        return None

# --- BLOK TESTOWY ---
# Ten kod wykona się tylko, gdy uruchomisz ten plik bezpośrednio (np. wpisując `python database.py` w terminalu)
if __name__ == "__main__":
    print("⏳ Łączenie z bazą danych Neon...")

    conn = get_db_connection()

    if conn:
        print("✅ Połączono pomyślnie!\n")
        try:
            with conn.cursor() as cursor:
                # Testowe zapytanie - sprawdzamy naszą tabelę z potrzebami
                cursor.execute("SELECT * FROM potrzeba;")
                wyniki = cursor.fetchall()

                print("📋 Dostępne kategorie potrzeb w bazie:")
                for wiersz in wyniki:
                    # Dzięki RealDictCursor możemy odpytywać po nazwach kolumn:
                    print(f"ID: {wiersz['id_potrzeba']} | Nazwa: {wiersz['nazwa_potrzeba']}")

        except Exception as e:
            print(f"❌ Błąd podczas wykonywania zapytania: {e}")
        finally:
            # Zawsze pamiętajcie o zamykaniu połączenia po wykonaniu pracy!
            conn.close()
            print("\n🔌 Połączenie zamknięte.")
    else:
        print("❌ Nie udało się połączyć. Sprawdź link w pliku .env i swoje połączenie z internetem.")
