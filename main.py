from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
import requests
import re

# Função para baixar o vídeo
def download_video(video_url, folder='videos'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    video_name = video_url.split('/')[-1].split('?')[0]
    video_name = re.sub(r'[<>:"/\\|?*]', '_', video_name)
    video_path = os.path.join(folder, video_name)

    # Verifica se o vídeo já foi baixado
    if not os.path.exists(video_path):
        response = requests.get(video_url, stream=True)
        with open(video_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f'Baixado: {video_path}')
    else:
        print(f'Vídeo já baixado: {video_path}')

# Caminho absoluto para o ChromeDriver
service = Service('chromedriver-win64/chromedriver-win64/chromedriver.exe')

# Definir opções do Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')  # Executa em modo headless
chrome_options.add_argument('--disable-gpu')  # Desativa GPU para melhorar a performance no modo headless
chrome_options.add_argument('--window-size=1920,1080')

# Inicia o driver com as opções
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL da conta do Kwai
url = 'https://www.kwai.com/@cenastopsnarra'
driver.get(url)

# Aguarde um tempo para a página carregar
time.sleep(4)

# Conjunto para armazenar URLs de vídeos já baixados
downloaded_videos = set()

# Inicialize o ActionChains para simular o movimento do mouse
actions = ActionChains(driver)

# Contador para verificar se os vídeos estão sendo carregados
scroll_attempts = 0
max_scroll_attempts = 10  # Limite de tentativas de rolagem sem novos vídeos

# Configuração da rolagem gradual
scroll_increment = 500  # Quantidade de pixels para rolar por vez
scroll_position = 0  # Posição inicial
previous_video_count = 0  # Quantidade de vídeos processados anteriormente

try:
    while True:
        # Encontre todos os elementos 'video-content' que estão visíveis
        video_contents = driver.find_elements(By.CLASS_NAME, 'video-content')

        # Iterar apenas sobre os novos vídeos que foram carregados após a última rolagem
        for i in range(previous_video_count, len(video_contents)):
            video_box = video_contents[i]
            try:
                # Simula o movimento do mouse para passar sobre o vídeo
                actions.move_to_element(video_box).perform()
                time.sleep(1)  # Dê tempo para o vídeo carregar

                # Tente encontrar o atributo 'src' ou 'data-src'
                video_element = video_box.find_element(By.TAG_NAME, 'video')
                video_url = video_element.get_attribute('src')

                # Verifica se o URL já foi baixado
                if video_url and video_url not in downloaded_videos:
                    print(f'Encontrado vídeo: {video_url}')
                    download_video(video_url)
                    driver.save_screenshot('screenie.png')
                    downloaded_videos.add(video_url)

            except Exception as e:
                print(f"Erro ao localizar o vídeo: {e}")

        # Atualizar o contador de vídeos processados
        previous_video_count = len(video_contents)

        # Rola a página gradualmente para carregar mais vídeos
        scroll_position += scroll_increment  # Aumenta a posição de rolagem
        driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
        print(f"Rolando para posição: {scroll_position}")
        driver.save_screenshot('screenie.png')
        time.sleep(5)  # Tempo para novos vídeos carregarem

        # Verifique se novos vídeos foram carregados
        new_video_contents = driver.find_elements(By.CLASS_NAME, 'video-content')
        if len(new_video_contents) <= len(video_contents):
            scroll_attempts += 1
        else:
            scroll_attempts = 0  # Reinicie o contador de tentativas de rolagem

        # Se o número de tentativas sem novos vídeos for maior que o limite, saia do loop
        if scroll_attempts >= max_scroll_attempts:
            print("Fim da página ou limite de tentativas sem novos vídeos alcançado.")
            break

except Exception as e:
    print(f"Erro: {e}")

finally:
    driver.quit()
