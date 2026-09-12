from database import get_db_connection, init_db

# Echte Fragen-Datenbank mit unterschiedlichen Kategorien & Schwierigkeiten
QUESTIONS_DATA = [
    # --- KATEGORIE: Sprichwörter & Alltag ---
    {
        "category": "Literatur & Sprichwörter",
        "difficulty": "Easy",
        "question_text": "Wie geht das Sprichwort weiter: 'Lügen haben ...'?",
        "option_a": "rote Ohren",
        "option_b": "kurze Beine",
        "option_c": "lange Nase",
        "option_d": "schnelle Füße",
        "correct_option": "B",
        "explanation": "Das bekannte Sprichwort bedeutet, dass Unwahrheiten schnell auffliegen."
    },
    {
        "category": "Literatur & Sprichwörter",
        "difficulty": "Medium",
        "question_text": "Was bedeutet die Redewendung 'Eulen nach Athen tragen'?",
        "option_a": "Etwas Unnützes tun",
        "option_b": "Einen Streit schlichten",
        "option_c": "Sehr klug sein",
        "option_d": "Nachts arbeiten",
        "correct_option": "A",
        "explanation": "Athen hatte damals schon viele Eulen (Symbol der Weisheit), daher war es überflüssig, weitere dorthin zu bringen."
    },
    {
        "category": "Literatur & Sprichwörter",
        "difficulty": "Hard",
        "question_text": "Aus welchem Werk stammt das Zitat 'Der Worte sind genug gewechselt, lasst mich auch endlich Taten sehn!'?",
        "option_a": "Schillers 'Götz von Berlichingen'",
        "option_b": "Goethes 'Faust I'",
        "option_c": "Lessings 'Nathan der Weise'",
        "option_d": "Heines 'Deutschland. Ein Wintermärchen'",
        "correct_option": "B",
        "explanation": "Das Zitat stammt aus dem Vorspiel auf dem Theater in Goethes Tragödie Faust I."
    },

    # --- KATEGORIE: Geografie ---
    {
        "category": "Geografie",
        "difficulty": "Easy",
        "question_text": "Welcher Fluss fließt durch die Stadt Köln?",
        "option_a": "Donau",
        "option_b": "Elbe",
        "option_c": "Rhein",
        "option_d": "Mosel",
        "correct_option": "C",
        "explanation": "Der Rhein teilt Köln in die linke und die rechtsrheinische Seite ('Schäl Sick')."
    },
    {
        "category": "Geografie",
        "difficulty": "Medium",
        "question_text": "Welches deutsche Bundesland hat die meisten Einwohner?",
        "option_a": "Bayern",
        "option_b": "Baden-Württemberg",
        "option_c": "Niedersachsen",
        "option_d": "Nordrhein-Westfalen",
        "correct_option": "D",
        "explanation": "Mit knapp 18 Millionen Einwohnern ist Nordrhein-Westfalen das bevölkerungsreichste Bundesland."
    },
    {
        "category": "Geografie",
        "difficulty": "Hard",
        "question_text": "An welchem Fluss liegt die baden-württembergische Stadt Heidelberg?",
        "option_a": "Neckar",
        "option_b": "Main",
        "option_c": "Jagst",
        "option_d": "Enz",
        "correct_option": "A",
        "explanation": "Heidelberg liegt am Neckar, der kurz danach bei Mannheim in den Rhein mündet."
    },

    # --- KATEGORIE: Geschichte ---
    {
        "category": "Geschichte",
        "difficulty": "Easy",
        "question_text": "In welchem Jahr fiel die Berliner Mauer?",
        "option_a": "1985",
        "option_b": "1989",
        "option_c": "1990",
        "option_d": "1992",
        "correct_option": "B",
        "explanation": "Am Abend des 9. November 1989 wurde die Berliner Mauer geöffnet."
    },
    {
        "category": "Geschichte",
        "difficulty": "Medium",
        "question_text": "Wer war der erste Bundeskanzler der Bundesrepublik Deutschland?",
        "option_a": "Willy Brandt",
        "option_b": "Helmut Schmidt",
        "option_c": "Konrad Adenauer",
        "option_d": "Ludwig Erhard",
        "correct_option": "C",
        "explanation": "Konrad Adenauer war von 1949 bis 1963 der erste Bundeskanzler der BRD."
    },
    {
        "category": "Geschichte",
        "difficulty": "Hard",
        "question_text": "In welchem Jahr wurde die D-Mark in den westlichen Besatzungszonen eingeführt?",
        "option_a": "1945",
        "option_b": "1948",
        "option_c": "1950",
        "option_d": "1953",
        "correct_option": "B",
        "explanation": "Die Währungsreform am 20. Juni 1948 führte die Deutsche Mark ein."
    },

    # --- KATEGORIE: Musik & Kultur ---
    {
        "category": "Musik & Kultur",
        "difficulty": "Easy",
        "question_text": "Welcher Sänger wurde als 'King of Rock 'n' Roll' bekannt?",
        "option_a": "Buddy Holly",
        "option_b": "Chuck Berry",
        "option_c": "Elvis Presley",
        "option_d": "Johnny Cash",
        "correct_option": "C",
        "explanation": "Elvis Presley gilt bis heute als der 'King of Rock 'n' Roll'."
    },
    {
        "category": "Musik & Kultur",
        "difficulty": "Medium",
        "question_text": "Von welchem Komponisten stammt die berühmte 'Ode an die Freude'?",
        "option_a": "Wolfgang Amadeus Mozart",
        "option_b": "Ludwig van Beethoven",
        "option_c": "Johann Sebastian Bach",
        "option_d": "Franz Schubert",
        "correct_option": "B",
        "explanation": "Beethoven vertonte Schillers Gedicht im 4. Satz seiner 9. Sinfonie."
    },

    # --- KATEGORIE: Essen & Trinken ---
    {
        "category": "Essen & Trinken",
        "difficulty": "Easy",
        "question_text": "Aus welchem Land stammt das Gericht Paella ursprünglich?",
        "option_a": "Italien",
        "option_b": "Griechenland",
        "option_c": "Frankreich",
        "option_d": "Spanien",
        "correct_option": "D",
        "explanation": "Paella ist ein traditionelles Reisgericht aus der Region Valencia in Spanien."
    }
]


def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    imported_count = 0

    for item in QUESTIONS_DATA:
        cat_name = item['category']

        # 1. Kategorie anlegen, falls noch nicht vorhanden
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (cat_name,))
        cursor.execute('SELECT id FROM categories WHERE name = ?', (cat_name,))
        category_id = cursor.fetchone()['id']

        # 2. Prüfen, ob Frage schon existiert (Vermeidet Duplikate)
        cursor.execute('SELECT id FROM questions WHERE question_text = ?', (item['question_text'],))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO questions 
                (category_id, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                category_id,
                item['difficulty'],
                item['question_text'],
                item['option_a'],
                item['option_b'],
                item['option_c'],
                item['option_d'],
                item['correct_option'],
                item['explanation']
            ))
            imported_count += 1

    conn.commit()
    conn.close()
    print(f"✅ {imported_count} echte Fragen wurden erfolgreich in 'quiz.db' gespeichert!")


if __name__ == "__main__":
    seed_database()