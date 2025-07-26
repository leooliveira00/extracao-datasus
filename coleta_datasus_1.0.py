from ftplib import FTP
from datetime import datetime
from dateutil.relativedelta import relativedelta
import smtplib
from email.message import EmailMessage
import os
import datasus_dbc
from dbfread import DBF
import pandas as pd
import shutil
import json
import sys

"""
    ---| 18/06/2025 |---
Programa criado para automatizar a extração mensal de arquivos do DataSUS e disponibilizar para serem carregados no PowerBi.
Por: Leonardo Sousa


"""

# === CONFIGURAÇÕES FTP & Diretórios ===
ftp_host = "ftp.datasus.gov.br"
ftp_dir = "/dissemin/publicos/SIHSUS/200801_/Dados/"

base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))


destino_local = os.path.join(base_dir, "Download")
destino_final_csv = os.path.join(base_dir, "DataSus")
log_path = os.path.join(base_dir, "log.txt")

#Verificação para permitir execução apenas uma vez por mês
marcador_path = os.path.join(base_dir, "controle_execucao.json")
mes_atual = datetime.now().strftime("%Y-%m")

if os.path.exists(marcador_path):
    with open(marcador_path, "r") as f:
        ultimo = json.load(f).get("ultimo_processamento")
        if ultimo == mes_atual:
            print(f"Processo já executado em {mes_atual}. Encerrando.")
            exit()

# Configurações de e-mail SMTP
EMAIL_REMETENTE = ""
EMAIL_SENHA = ""  
EMAIL_DESTINATARIOS = []
SMTP_SERVER = ""
SMTP_PORT = 

# Configurações de LOG 
log = []
def logar(msg):
    print(msg)
    log.append(f"{datetime.now()} - {msg}")

sucesso = True

    # === CÁLCULO SUFIXO ===

try:
    
    data_atual = datetime.now()
    data_alvo = data_atual - relativedelta(months=2)
    sufixo = f"{str(data_alvo.year)[-2:]}{data_alvo.month:02d}.dbc"
    #sufixo = "SPGO2504.dbc"
    
    os.makedirs(destino_local, exist_ok=True)
    os.makedirs(destino_final_csv, exist_ok=True)

    logar(f"Conectando ao FTP: {ftp_host}")
    ftp = FTP(ftp_host)
    ftp.login()
    ftp.cwd(ftp_dir)
    logar(f"Navegando até o diretório: {ftp_dir}")

    arquivos = ftp.nlst()
    filtrados = [f for f in arquivos if f.startswith("SP") and f.endswith(sufixo)]

    logar(f"Arquivos encontrados com sufixo '{sufixo}': {len(filtrados)}")

    if not filtrados:
        mensagem = "Nenhum arquivo com o sufixo esperado foi encontrado.\n"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logar(mensagem)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp}] {mensagem}\n")
        sys.exit(1)

    for nome_arquivo in filtrados:
        caminho_local = os.path.join(destino_local, nome_arquivo)
        with open(caminho_local, 'wb') as f:
            logar(f"Baixando: {nome_arquivo}")
            ftp.retrbinary(f'RETR {nome_arquivo}', f.write)

    ftp.quit()
    logar("Download concluído.")

    # === CONVERSÃO ===
    for nome_arquivo in os.listdir(destino_local):
        if nome_arquivo.lower().endswith('.dbc'):
            try:
                caminho_dbc = os.path.join(destino_local, nome_arquivo)
                nome_base = os.path.splitext(nome_arquivo)[0]
                caminho_dbf = os.path.join(destino_local, f"{nome_base}.dbf")
                caminho_csv = os.path.join(destino_local, f"{nome_base}.csv")

                logar(f"Convertendo {nome_arquivo} para DBF...")
                datasus_dbc.decompress(caminho_dbc, caminho_dbf)

                logar(f"Lendo DBF e salvando como CSV...")
                dbf = DBF(caminho_dbf, encoding='latin1')
                df = pd.DataFrame(iter(dbf))
                df.to_csv(caminho_csv, index=False)

                os.remove(caminho_dbf)
                os.remove(caminho_dbc)

                destino_final = os.path.join(destino_final_csv, f"{nome_base}.csv")
                shutil.move(caminho_csv, destino_final)

                logar(f"Arquivo convertido e movido: {destino_final}")
            except Exception as e:
                sucesso = False
                logar(f"Erro ao processar {nome_arquivo}: {e}")

except Exception as e:
    sucesso = False
    logar(f"Falha no processo: {e}")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log))
        sys.exit(1)

# === SALVA O LOG ===
with open(log_path, "w", encoding="utf-8") as f:
    f.write("\n".join(log))
    
    
with open(marcador_path, "w") as f:
    json.dump({"ultimo_processamento": mes_atual}, f)


# === ENVIO E-MAIL DE CONCLUSÃO ===
try:
    assunto = "DATASUS - O Processo de Extração dos arquivos foi concluído com sucesso!" if sucesso else "DATASUS - A extração dos arquivos falhou"
    corpo = "Prezado (a),\n\nSegue em anexo o log do processo automático de extração e conversão dos arquivos do DATASUS.\n\nAtenciosamente,\nTI Scitech"

    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = ", ".join(EMAIL_DESTINATARIOS)
    msg.set_content(corpo)

    with open(log_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="text", subtype="plain", filename="log.txt")
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_REMETENTE, EMAIL_SENHA)
        smtp.send_message(msg)

    logar("E-mail enviado com sucesso.")

except Exception as e:
    logar(f"Erro ao enviar e-mail: {e}")

finally:
    # CRIANDO LOG AO FIM
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log))

    with open(marcador_path, "w") as f:
        json.dump({"ultimo_processamento": mes_atual}, f)
