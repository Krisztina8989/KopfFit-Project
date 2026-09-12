from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import random
import time
import json
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = "senioren_quiz_geheimer_schluessel"

# Automatische Abmeldung beim Schließen des Browsers
app.config['SESSION_PERMANENT'] = False

init_db()

# punktevergabe
QUESTION_POINTS = [5, 10, 20, 40, 30, 20, 10, 5, 5, 10]

#  dekorator für login schutz
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Bitte melden Sie sich zuerst an.", "warning")
            return redirect(url_for('spiel_starten'))
        return f(*args, **kwargs)
    return decorated_function

# authentifizierung

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        flash("Bitte geben Sie Benutzername und Passwort ein.", "danger")
        return redirect(url_for('spiel_starten'))

    pwd_hash = generate_password_hash(password)
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, pwd_hash))
        conn.commit()
        conn.close()
        flash("Registrierung erfolgreich! Bitte melden Sie sich an.", "success")
    except sqlite3.IntegrityError:
        conn.close()
        flash("Dieser Benutzername ist bereits vergeben.", "danger")

    return redirect(url_for('spiel_starten'))


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash(f"Willkommen zurück, {user['username']}!", "success")
    else:
        flash("Ungültige Anmeldedaten.", "danger")

    return redirect(url_for('spiel_starten'))


@app.route('/logout')
def logout():
    session.clear()
    flash("Sie wurden erfolgreich abgemeldet.", "info")
    return redirect(url_for('spiel_starten'))

#statische_seiten

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uber_uns')
def uber_uns():
    return render_template('uber_uns.html')

@app.route('/kontakt', methods=['GET', 'POST'])
def kontakt():
    success = False
    if request.method == 'POST':
        success = True
    return render_template('kontakt.html', success=success)

#spiel_starten, team_verwaltung

@app.route('/spiel_starten', methods=['GET', 'POST'])
def spiel_starten():
    user_id = session.get('user_id')
    teams = []

    if user_id:
        conn = get_db_connection()

        if request.method == 'POST':
            new_team = request.form.get('new_team_name')
            if new_team:
                try:
                    conn.execute('INSERT INTO teams (user_id, team_name) VALUES (?, ?)', (user_id, new_team.strip()))
                    conn.commit()
                except sqlite3.IntegrityError:
                    flash("Dieses Team existiert bereits.", "warning")
                conn.close()
                return redirect(url_for('spiel_starten'))

            #team_name_ändern
            teams_in_db = conn.execute('SELECT * FROM teams WHERE user_id = ?', (user_id,)).fetchall()
            for t in teams_in_db:
                updated_name = request.form.get(f'team_name_{t["id"]}')
                if updated_name and updated_name.strip() != t['team_name']:
                    try:
                        conn.execute('UPDATE teams SET team_name = ? WHERE id = ?', (updated_name.strip(), t['id']))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        pass

            #spiel_mit_gewählte_teams_starten
            selected_team_ids = request.form.getlist('selected_teams')
            difficulty = request.form.get('difficulty')

            if len(selected_team_ids) >= 1 and difficulty:
                session['teams'] = [int(tid) for tid in selected_team_ids]
                session['difficulty'] = difficulty
                session['round'] = 1
                session['scores'] = {str(tid): 0 for tid in session['teams']}
                session['speed_scores'] = {str(tid): 0 for tid in session['teams']}
                session['used_categories'] = []
                conn.close()
                return redirect(url_for('choose_category'))

        teams = conn.execute('SELECT * FROM teams WHERE user_id = ?', (user_id,)).fetchall()
        conn.close()

    return render_template('spiel_starten.html', teams=teams)

#kategorie_auswahl_durch_zufallsteam

@app.route('/choose_category', methods=['GET', 'POST'])
@login_required
def choose_category():
    current_round = session.get('round', 1)
    if current_round > 5:
        return redirect(url_for('final_results'))

    conn = get_db_connection()

    used_cats = session.get('used_categories', [])
    if used_cats:
        placeholders = ','.join('?' * len(used_cats))
        categories = conn.execute(f'SELECT * FROM categories WHERE id NOT IN ({placeholders})', used_cats).fetchall()
    else:
        categories = conn.execute('SELECT * FROM categories').fetchall()

    if not categories:
        conn.close()
        return redirect(url_for('final_results'))

    if request.method == 'GET' and 'choosing_team_id' not in session:
        choosing_team_id = random.choice(session['teams'])
        session['choosing_team_id'] = choosing_team_id
    else:
        choosing_team_id = session.get('choosing_team_id', session['teams'][0])

    choosing_team = conn.execute('SELECT * FROM teams WHERE id = ?', (choosing_team_id,)).fetchone()

    if request.method == 'POST':
        cat_id = int(request.form.get('category_id'))
        category = conn.execute('SELECT * FROM categories WHERE id = ?', (cat_id,)).fetchone()

        session['current_category_id'] = category['id']
        session['current_category_name'] = category['name']
        session['used_categories'].append(category['id'])
        session.pop('choosing_team_id', None)

        team_ids = session['teams']
        team_placeholders = ','.join('?' * len(team_ids))
        sql = f'''
            SELECT * FROM questions 
            WHERE category_id = ? 
              AND difficulty = ? 
              AND id NOT IN (
                  SELECT question_id 
                  FROM played_questions 
                  WHERE team_id IN ({team_placeholders}) 
                    AND played_at >= DATE('now', '-2 months')
              )
            ORDER BY RANDOM() 
            LIMIT 10
        '''
        params = [category['id'], session['difficulty']] + team_ids
        questions = conn.execute(sql, params).fetchall()

        if len(questions) < 10:
            sql_fallback = 'SELECT * FROM questions WHERE category_id = ? AND difficulty = ? ORDER BY RANDOM() LIMIT 10'
            questions = conn.execute(sql_fallback, (category['id'], session['difficulty'])).fetchall()

        conn.close()

        session['round_questions'] = [q['id'] for q in questions]
        session['question_index'] = 0
        return redirect(url_for('show_question'))

    conn.close()
    return render_template('choose_category.html', categories=categories, choosing_team=choosing_team, round_num=current_round)

# frage_anzeigen_auswertung

@app.route('/question', methods=['GET', 'POST'])
@login_required
def show_question():
    q_ids = session.get('round_questions', [])
    q_idx = session.get('question_index', 0)

    if q_idx >= len(q_ids):
        return redirect(url_for('leaderboard'))

    conn = get_db_connection()
    question = conn.execute('SELECT * FROM questions WHERE id = ?', (q_ids[q_idx],)).fetchone()
    teams = conn.execute(f'SELECT * FROM teams WHERE id IN ({",".join("?" * len(session["teams"]))})',
                         session['teams']).fetchall()

    if request.method == 'POST':
        answers = {}
        team_times = {}

        points_for_this_question = QUESTION_POINTS[q_idx] if q_idx < len(QUESTION_POINTS) else 10

        for team in teams:
            ans = request.form.get(f'answer_team_{team["id"]}')
            t_time = float(request.form.get(f'time_team_{team["id"]}', 999.0))
            answers[team['id']] = ans
            team_times[team['id']] = t_time

            if ans == question['correct_option']:
                session['scores'][str(team['id'])] = session['scores'].get(str(team['id']), 0) + points_for_this_question

            conn.execute('INSERT INTO played_questions (team_id, question_id) VALUES (?, ?)',
                         (team['id'], question['id']))

        conn.commit()
        conn.close()

        correct_teams = [t_id for t_id in session['teams'] if answers.get(t_id) == question['correct_option']]
        correct_teams.sort(key=lambda t_id: team_times.get(t_id, 999.0))

        speed_bonus = [10, 5, 2]
        for idx, t_id in enumerate(correct_teams):
            if idx < len(speed_bonus):
                session['speed_scores'][str(t_id)] = session['speed_scores'].get(str(t_id), 0) + speed_bonus[idx]

        session['question_index'] += 1
        return render_template('answer.html', question=question, answers=answers, teams=teams)

    conn.close()
    return render_template('game.html', question=question, teams=teams, start_time=time.time(), question_points=QUESTION_POINTS[q_idx])

#zwischenstand_tafel

@app.route('/leaderboard')
@login_required
def leaderboard():
    conn = get_db_connection()
    teams = conn.execute(f'SELECT * FROM teams WHERE id IN ({",".join("?" * len(session["teams"]))})',
                         session['teams']).fetchall()
    conn.close()

    scores = session.get('scores', {})
    team_ranks = []
    for t in teams:
        team_ranks.append({
            'name': t['team_name'],
            'score': scores.get(str(t['id']), 0)
        })
    team_ranks.sort(key=lambda x: x['score'], reverse=True)

    session['round'] += 1

    return render_template('leaderboard.html', ranks=team_ranks, current_round=session['round'] - 1)

#endergebnis

@app.route('/final')
@login_required
def final_results():
    conn = get_db_connection()
    teams = conn.execute(f'SELECT * FROM teams WHERE id IN ({",".join("?" * len(session["teams"]))})',
                         session['teams']).fetchall()

    scores = session.get('scores', {})
    speed_scores = session.get('speed_scores', {})

    final_list = []
    for t in teams:
        h_score = scores.get(str(t['id']), 0)
        s_score = speed_scores.get(str(t['id']), 0)
        final_list.append({
            'name': t['team_name'],
            'main_score': h_score,
            'speed_score': s_score,
            'total_score': h_score + s_score
        })

    final_list.sort(key=lambda x: x['total_score'], reverse=True)
    winner_name = final_list[0]['name'] if final_list else "Kein Team"

    conn.execute('INSERT INTO game_results (user_id, winner_team, scores_json) VALUES (?, ?, ?)',
                 (session['user_id'], winner_name, json.dumps(final_list)))
    conn.commit()
    conn.close()

    return render_template('final.html', results=final_list)


if __name__ == '__main__':
    app.run(debug=True)