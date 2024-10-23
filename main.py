import requests
import os
import re
from utils import choose_trail_course, display_trail_course, page_course, video_url, download_video, headers
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


def normalize_str(normalize_me):
    return " ".join(re.sub(r'[<>:!"/\\|?*]', '', normalize_me)
                    .replace('\t', '')
                    .replace('\n', '')
                    .replace('.', '')
                    .split(' ')).strip()


def process_lesson(lesson, model_name, path_long, session):
    lesson_name = normalize_str(str(lesson["lesson_name"]))
    lesson_url = lesson["lesson_url"]
    directory_lesson = os.path.join(path_long, model_name, lesson_name)
    os.makedirs(directory_lesson, exist_ok=True)
    
    if  os.path.exists(f'{directory_lesson}/aula.mp4'):
        print(f"Aula baixada {model_name}/{lesson_name}, indo pra próxima...")
        pass
    else:
        url_video_lesson = video_url(session, lesson_url)
        if url_video_lesson is not None:
            download_video(url_video_lesson, directory_lesson, headers)
        else:
            pass
    
    if  os.path.exists(f'{directory_lesson}/descrição.html'):
        pass
    else:
        html = session.get(lesson_url)
        with open(f'{directory_lesson}/descrição.html', 'w', encoding='utf-8') as file:
          file.write(html.text)
  
    



def execution(modulos, materiais_link, path, session):
    path_long = path
    os.makedirs(path_long, exist_ok=True)

    if not os.path.exists(f'{path_long}/Materiais.txt'):
        with open(f'{path_long}/Materiais.txt', 'w') as file:
            file.write(materiais_link)

    # Usar ThreadPoolExecutor para processar lições em paralelo
    with ThreadPoolExecutor(max_workers=7) as executor:  # Limite de threads simultâneas
        futures = []

        for m in modulos:
            for model_name, lessons in m.items():
                model_name = normalize_str(str(model_name))
                os.makedirs(os.path.join(path_long, model_name), exist_ok=True)

                # Adicionar tarefas de download ao pool de threads
                for lesson in lessons:
                    futures.append(executor.submit(process_lesson, lesson, model_name, path_long, session))

        # Acompanhar o progresso usando as_completed
        for future in as_completed(futures):
            try:
                future.result()  # Pega o resultado da execução, tratando exceções
            except Exception as e:
                print(f"Erro durante o processamento de uma lição: {e}")


if __name__ == "__main__":
    # Conexão para o Asimov
    User_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    url = 'https://hub.asimov.academy/login'
    email = ''
    pwd = ''
    payload = {'login': email, 'password': pwd}

    # Salvar sessão de conexão
    session = requests.Session()
    session.headers.update({'User-Agent': User_agent})

    # Listar trilhas e cursos
    r = session.post(url, data=payload)
    url_courses = 'https://hub.asimov.academy/trilhas/'
    page_trails = session.get(url_courses)
    list_trail = display_trail_course(page_trails, 'n')
    name_trail, url_trail = choose_trail_course(list_trail)
    os.system('cls')

    # Escolher modo de download
    # choose_download = input("Voce deseja baixar todos cursos da trilha? (y/n)\n").lower()
    choose_download = 'y'
    os.system('cls')

    if choose_download == 'y':
        page_courses = session.get(url_trail)
        list_courses = display_trail_course(page_courses, 'y')
        i = 0
        for course in list_courses:
            i += 1
            for name, value in course.items():
                url_course = value
                page_course_html = session.get(url_course)
                modulos, name_course, materiais_link = page_course(page_course_html)
                name_course = normalize_str(name_course)
                path = f"cursos/{normalize_str(name_trail)}/{i} - {name_course}"
                execution(modulos, materiais_link, path, session)
    else:
        page_courses = session.get(url_trail)
        list_courses = display_trail_course(page_courses, 'n')
        element_name, element_url = choose_trail_course(list_courses)
        os.system('cls')
        page_course_html = session.get(element_url)
        modulos, name_course, materiais_link = page_course(page_course_html)
        name_course = normalize_str(name_course)
        path = f"cursos/{name_course}"
        execution(modulos, materiais_link, path, session)
