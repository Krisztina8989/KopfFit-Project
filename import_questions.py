import json
from database import get_db_connection, init_db

FIXED_CATEGORIES = [
    "Geschichte",
    "Geografie",
    "Musik & Kultur",
    "Natur & Wissenschaft",
    "Alltag & Haushalt",
    "Film & Fernsehen",
    "Essen & Trinken",
    "Sport & Spiele",
    "Tiere & Pflanzen",
    "Literatur & Sprichwörter"
]

def import_questions():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cat_ids = {}
    for cat_name in FIXED_CATEGORIES:
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (cat_name,))
        cursor.execute('SELECT id FROM categories WHERE name = ?', (cat_name,))
        cat_ids[cat_name] = cursor.fetchone()['id']

    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            questions = json.load(f)
    except FileNotFoundError:
        print("❌ 'questions.json' wurde nicht gefunden!")
        return

    count = 0
    for q in questions:
        if q['category'] in cat_ids:
            cursor.execute('''
                INSERT INTO questions 
                (category_id, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cat_ids[q['category']],
                q['difficulty'],
                q['question_text'],
                q['option_a'],
                q['option_b'],
                q['option_c'],
                q['option_d'],
                q['correct_option'],
                q['explanation']
            ))
            count += 1

    conn.commit()
    conn.close()
    print(f"✅ {count} Fragen wurden erfolgreich den 10 Kategorien zugeordnet!")

if __name__ == "__main__":
    import_questions()