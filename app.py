import requests
from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = 'anime_quiz_secret_key'

def get_random_anime():
    """Random anime with synopsis"""
    max_attempts = 20
    attempts = 0

    while attempts < max_attempts:
        response = requests.get("https://api.jikan.moe/v4/random/anime")

        if response.status_code == 200:
            data = response.json()
            anime_data = data['data']

            #Check if there a description and synopsys
            synopsis = anime_data.get('synopsis')
            title = anime_data.get('title')

            if synopsis and title and len(synopsis) > 100:
                return {
                    'title': title,
                    'synopsis': synopsis,
                    'score': anime_data.get('score'),
                    'year': anime_data.get('year'),
                    'image': anime_data['images']['jpg']['image_url'],
                    'url': anime_data['url']
                }
        
        attempts += 1

    return None

def generate_wrong_answer():
    '''Generating wrong varios answer'''
    wron_answer = []
    attempts = 0

    while len(wron_answer) < 3 and attempts < 15:
        response = requests.get('https://api.jikan.moe/v4/random/anime')

        if response.status_code == 200:
            data = response.json()
            title = data['data'].get('title')

            if title and title not in wron_answer:
                wron_answer.append(title)

        attempts += 1
    
    #if not enogh various, add harvested
    backup_titles = [
        "Attack on Titan", "Naruto", "One Piece", "Dragon Ball Z",
        "Death Note", "Fullmetal Alchemist", "My Hero Academia",
        "Demon Slayer", "One Punch Man", "Tokyo Ghoul"
    ]

    while len(wron_answer) < 3:
        wron_answer.append(random.choice(backup_titles))
    
    return wron_answer[:3]

@app.route('/')
def quiz_start():
    '''Main menu of quiz'''

    session.clear()
    session['score'] = 0
    session['total_questions'] = 0

    return render_template('quiz_start.html')

@app.route('/question')
def quiz_quiestion():
    '''Generate question'''
    anime = get_random_anime()

    if not anime:
        return 'Ошибка получения данных. Попробуйте еще раз.', 500
    
    #Generate various answer
    wrong_answer = generate_wrong_answer()
    all_answer = wrong_answer + [anime['title']]
    random.shuffle(all_answer)

    session['correct_answer'] = anime['title']
    session['current_anime'] = anime

    quiz_data = {
        'synopsis': anime['synopsis'],
        'answers': all_answer,
        'score': session.get('score', 0),
        'total': session.get('total_questions', 0)
    }

    return render_template('quiz_question.html', quiz=quiz_data)

@app.route('/answer', methods=['POST'])
def quiz_answer():
    """Check user answer"""
    user_answer = request.form.get('answer')
    correct_answer = session.get('correct_answer')
    current_anime = session.get('current_anime')
    
    # Увеличиваем счетчик вопросов
    session['total_questions'] = session.get('total_questions', 0) + 1
    
    is_correct = user_answer == correct_answer
    
    if is_correct:
        session['score'] = session.get('score', 0) + 1
    
    result_data = {
        'is_correct': is_correct,
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'anime': current_anime,
        'score': session.get('score', 0),
        'total': session.get('total_questions', 0)
    }
    
    return render_template('quiz_result.html', result=result_data)

if __name__ == '__main__':
    app.run(debug=True)