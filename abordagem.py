import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

opcoes_chrome = webdriver.ChromeOptions()
opcoes_chrome.add_argument("--ignore-certificate-errors")
driver = webdriver.Chrome(options=opcoes_chrome)

def aguardar_qr_code():
    input("Por favor, leia o QR code no WhatsApp Web e pressione Enter aqui para continuar.")
    print("QR code lido com sucesso. Continuando...")

def obter_saudacao():
    hora_atual = datetime.now().hour
    if hora_atual < 12:
        return "bom dia"
    elif 12 <= hora_atual < 18:
        return "boa tarde"
    else:
        return "boa noite"

def enviar_mensagem_whatsapp(telefone, mensagem):
    url = f"https://web.whatsapp.com/send?phone={telefone}"
    driver.get(url)
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
        )
        textarea = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
        textarea.send_keys(mensagem)
        time.sleep(2)
        textarea.send_keys(Keys.ENTER)
        time.sleep(5)
        print(f"Mensagem enviada para {telefone}.")
        time.sleep(50)
        return True
    except TimeoutException:
        try:
            error_message = driver.find_element(By.XPATH, "//div[contains(text(),'O número de telefone compartilhado via URL é inválido')]")
            print(f"Número {telefone} não está no WhatsApp.")
        except NoSuchElementException:
            print(f"Tempo esgotado ao aguardar a presença do campo de mensagem para {telefone}.")
    except NoSuchElementException:
        print(f"Não foi possível encontrar o campo de mensagem para {telefone}.")
    except WebDriverException as e:
        print(f"Erro ao enviar mensagem para {telefone}: {e}")
    except Exception as e:
        print(f"Erro ao enviar mensagem para {telefone}: {e}")
    return False

def carregar_numeros_telefone(caminho_arquivo):
    telefones = []
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'r') as arquivo:
            for linha in arquivo:
                telefone = linha.strip()
                telefones.append(telefone)
    return telefones

def carregar_numeros_enviados(caminho_arquivo):
    numeros_enviados = set()
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'r') as arquivo:
            for linha in arquivo:
                telefone = linha.strip()
                numeros_enviados.add(telefone)
    return numeros_enviados

def salvar_numero_enviado(caminho_arquivo, telefone):
    with open(caminho_arquivo, 'a') as arquivo:
        arquivo.write(f"{telefone}\n")
    print(f"Número {telefone} salvo no arquivo de status.")

def main():
    arquivo_numeros = "numeros.txt"
    arquivo_status = "enviados.txt"
    saudacao = obter_saudacao()
    mensagem = f"Opa, {saudacao}! Encontrei o número da sua barbearia no google e gostaria de ajudar a atrair mais clientes pela internet. Teria interesse em conhecer meu trabalho?"

    telefones = carregar_numeros_telefone(arquivo_numeros)
    numeros_enviados = carregar_numeros_enviados(arquivo_status)

    primeira_vez = True
    for telefone in telefones:
        if telefone not in numeros_enviados:
            if primeira_vez:
                driver.get("https://web.whatsapp.com")
                aguardar_qr_code()
                primeira_vez = False
            if enviar_mensagem_whatsapp(telefone, mensagem):
                salvar_numero_enviado(arquivo_status, telefone)
                numeros_enviados.add(telefone)

    driver.quit()

if __name__ == "__main__":
    main()
