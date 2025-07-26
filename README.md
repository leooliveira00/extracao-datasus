

# Automação de Extração de Arquivos DataSUS

## Visão Geral
Este script Python automatiza a extração mensal, conversão e processamento de arquivos `.dbc` do servidor FTP do DataSUS. Ele baixa os arquivos, converte-os para o formato `.csv` e envia um e-mail com o status do processo e um arquivo de log anexado. O script foi projetado para simplificar um processo antes realizado manualmente, tornando-o eficiente e confiável para integração com ferramentas como o Power BI.

## Funcionalidades
- **Download via FTP**: Conecta-se ao servidor FTP do DataSUS para baixar arquivos `.dbc` com base em um sufixo calculado (dois meses antes da data atual).
- **Conversão de Arquivos**: Converte arquivos `.dbc` para `.dbf` e, em seguida, para `.csv` usando as bibliotecas `datasus_dbc` e `dbfread`.
- **Controle de Execução**: Garante que o script seja executado apenas uma vez por mês, utilizando um arquivo de controle em formato JSON.
- **Registro de Logs**: Mantém um log detalhado de todas as operações, salvo em `log.txt`.
- **Notificação por E-mail**: Envia um e-mail informando o sucesso ou falha do processo, com o log anexado.
- **Tratamento de Erros**: Inclui tratamento robusto de erros para registrar problemas e encerrar o processo de forma controlada.

## Pré-requisitos
- Python 3.8+
- Bibliotecas Python necessárias:
  ```bash
  pip install datasus-dbc dbfread pandas
  ```
- Acesso a um servidor SMTP para envio de e-mails.
- Permissões de escrita no diretório onde o script será executado.

## Configuração
1. **Clonar o Repositório**:
   ```bash
   git clone https://github.com/leooliveira00/extracao-datasus.git
   cd extracao-datasus
   ```

2. **Instalar Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar E-mail**:
   Atualize as seguintes variáveis em `coleta_datasus_1.0.py`:
   ```python
   EMAIL_REMETENTE = "seu-email@exemplo.com"
   EMAIL_SENHA = "sua-senha-de-email"
   EMAIL_DESTINATARIOS = ["destinatario1@exemplo.com", "destinatario2@exemplo.com"]
   SMTP_SERVER = "smtp.exemplo.com"
   SMTP_PORT = 587
   ```

4. **Configurar Diretórios**:
   Certifique-se de que o script tem permissão de escrita para criar os diretórios `Download`, `DataSus` e os arquivos de log no diretório de execução.

## Uso
1. Execute o script:
   ```bash
   python coleta_datasus_1.0.py
   ```
2. O script irá:
   - Verificar se já foi executado no mês atual.
   - Conectar-se ao servidor FTP do DataSUS (`ftp.datasus.gov.br`).
   - Baixar arquivos `.dbc` que começam com "SP" e correspondem ao sufixo calculado (ex.: `SP2510.dbc` para outubro de 2025).
   - Converter os arquivos `.dbc` para `.csv` e movê-los para o diretório `DataSus`.
   - Registrar todas as ações em `log.txt`.
   - Enviar um e-mail com o arquivo de log, indicando sucesso ou falha.

## Estrutura do Projeto
```
extracao-datasus/
├── coleta_datasus_1.0.py   # Script principal
├── Download/               # Armazenamento temporário de arquivos baixados
├── DataSus/                # Armazenamento final dos arquivos .csv
├── log.txt                 # Arquivo de log
├── controle_execucao.json  # Arquivo de controle de execução
└── README.md               # Este arquivo
```

## Observações
- O script busca arquivos de dois meses anteriores (ex.: em julho de 2025, ele baixa arquivos de maio de 2025).
- Certifique-se de que a biblioteca `datasus_dbc` é compatível com sua versão do Python.
- O diretório FTP está fixado em `/dissemin/publicos/SIHSUS/200801_/Dados/`. Atualize se necessário.
- Os logs de erro são salvos em `log.txt` e enviados por e-mail aos destinatários.

## Melhorias Futuras
- Adicionar suporte a um arquivo de configuração para FTP e e-mail.
- Implementar processamento paralelo para downloads e conversões mais rápidos.
- Incluir validações de dados nos arquivos `.csv` gerados.
- Adicionar testes unitários para funções críticas.

## Licença
Este projeto está licenciado sob a Licença MIT.

## Autor
Leonardo Sousa

