import re
from bs4 import BeautifulSoup
import yt_dlp


headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'identity;q=1, *;q=0',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Origin': 'https://iframe.mediadelivery.net',
    'Priority': 'i',
    'Range': 'bytes=0-',
    'Referer': 'https://iframe.mediadelivery.net/',
    'Sec-Fetch-Dest': 'video',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}


# criar classe de seleção de cursos, download, pagina de curso
def clean_course_string(input_string):
    # Passo 1: Remover a porcentagem no final e os espaços em branco após 'X - Y'
    result = re.sub(r'^\s*(\d+\s*-\s*\d+)\s*', r'\1 ', input_string)  # Limpa espaços após 'X - Y'
    result = re.sub(r'\s+\d+%$', '', result)  # Remove a porcentagem

    # Exibir o resultado
    return result.strip()


def choose_trail_course(list_options):
    # choose = int(input(f'\nEscolha um dos (cursos/trilhas) acima:\n'))
    choose = 3
    choose_number = (choose - 1)
    choose_course = list_options[choose_number]
    for name, value in choose_course.items():
        element_name = name
        element_url = value

    return element_name, element_url


def display_trail_course(page, resp):
    soup = BeautifulSoup(page.content, 'html.parser')
    elements = soup.find_all('article', class_=re.compile('course-card'))
    elements_list = []
    i = 0
    for element in elements:
        url_element = element.find('a').get('href')
        name_element = element.find('h2').get_text()
        elements_list.append({name_element: url_element})

    if resp == 'n':
        for t in elements_list:
            i += 1
            for name, url in t.items():
                print(f'{i}. {name}')
    return elements_list


def page_course(page_course):
    i = 0
    materiais_link_gd = None
    soup = BeautifulSoup(page_course.content, 'html.parser')
    name_course = f'{soup.find("h1").get_text()}'

    materias = soup.find_all('div', class_="flex flex-wrap gap-5 mt-9")
    for materia in materias:
        links = materia.find_all('a')
        for link in links:
            material_link = link.get('href')
            if 'drive.google.com'  in str(material_link):
                materiais_link_gd = f'Materiais do curso: {material_link}'
                print(materiais_link_gd)
    if not materiais_link_gd:
        materiais_link_gd = 'Nenhum material disponível'
    i = 0
    elements = soup.find_all('details', class_='p-0 details !bg-bg-100')
    modulos = []

    for element in elements:
        i += 1
        name_modulo = f'{i} - {element.find("summary").get_text().strip()}'
        name_modulo = clean_course_string(name_modulo)
        modulos.append({name_modulo: []})
        list_name_url_lesson = element.find_all('a')

        for line_elements in list_name_url_lesson:
            lesson_name = line_elements.get_text().strip()
            url_lesson = line_elements.get('href')

            modulos[i - 1][name_modulo].append({"lesson_name": lesson_name, "lesson_url": url_lesson})

    return modulos, name_course,  materiais_link_gd


def video_url(session, lesson_url):
    try:
        video_page = session.get(lesson_url)
        soup = BeautifulSoup(video_page.content, 'html.parser')
        list_video_url = soup.find_all('div', class_='[&>div]:!pt-[576px] md:[&>div]:!pt-[350px] sm:[&>div]:!pt-[250px] rounded-2xl mt-8 overflow-hidden')
        for list_video_url_2 in list_video_url:
            iframe_url = list_video_url_2.find('iframe').get('src')
            iframe_url_split = str(iframe_url).split('.')
            if iframe_url_split[1] == 'https://iframe' or iframe_url_split[1] == 'http://iframe':
                page_iframe = session.get(iframe_url)
                soup_iframe = BeautifulSoup(page_iframe.content, 'html.parser')
                video_url = soup_iframe.find('meta', property="og:video:url").get('content')
                url_end = str(video_url)
            else:
                url_end = iframe_url
        return url_end

    except:
        pass


def download_video(url_lesson, directory_lesson, headers):
    ydl_opts = {
        'outtmpl': f'{directory_lesson}/aula.mp4',  # Output path and filename template
        'format': 'bestvideo[height=720]+bestaudio/best[height=720]',
        'merge_output_format': 'mp4',  # Download the best available quality
        'http_headers': headers,
        'no_overwrites': True,
        'windows_filenames': True,
        'retries': 50,
        'trim_file_name': 249,
        'fragment_retries': 50,
        'extractor_retries': 50,
        'file_access_retries': 50,
        'concurrent_fragment_downloads': 10
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url_lesson])
