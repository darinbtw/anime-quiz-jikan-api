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

if __name__ == '__main__':
    app.run(debug=True)