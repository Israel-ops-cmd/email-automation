# EmailAutomation

Este repositório contém um software desenvolvido para automatizar o envio de emails em uma rotina corporativa. Antes da criação deste sistema, o processo era feito manualmente, consumindo mais de **uma hora por dia**. Com essa automação, o tempo foi reduzido para cerca de **cinco minutos**, otimizando tempo, reduzindo erros manuais e aumentando a produtividade.

## 🎯 Objetivo

Automatizar o envio diário de emails contendo informações personalizadas para diferentes destinatários, eliminando a necessidade de envio manual.

## 🧑‍💻 Aplicação na Empresa

O software foi desenvolvido para atender a uma demanda real dentro da empresa onde atuo, em que diariamente era necessário enviar dezenas de emails individualmente, preenchendo manualmente campos como nome e CNPJ. Agora, com a automação:

- O conteúdo dos emails é gerado dinamicamente a partir de uma base de dados;
- O envio é feito em lote com apenas um clique;
- Todo o processo é executado em menos de 5 minutos.

## 🛠️ Tecnologias Utilizadas

- Python 3.12  
- Bibliotecas: `smtplib`, `email`, `dotenv`, `pandas`, `jinja2`
- Gerador de executável: `PyInstaller`
- Ambiente isolado com `.env` para segurança de dados sensíveis

## 🔐 Segurança

O arquivo `.env` é ignorado pelo Git (via `.gitignore`) e **não é versionado**, garantindo a privacidade das informações sensíveis como login e senha de envio de email.

## 💡 Como Usar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/email-automation.git

2. Crie um arquivo .env na raiz com o seguinte conteúdo:
   ```bash
    EMAIL_REMETENTE=seu_email@gmail.com
    SENHA_APP=sua_senha_de_app
    ASSUNTO_EMAIL=Assunto do Email
    CORPO_EMAIL_HTML=Seu conteúdo HTML ou template

3. Instale as dependências:
  ```bash
  pip install -r requirements.txt
    ```

4. Execute o script main.py ou utilize o executável gerado (main.exe) para iniciar o envio.

📄 Registro de Software - Atividade Complementar
Este software está sendo utilizado como registro de atividade complementar no curso de Bacharelado em Tecnologia da Informação, pela Universidade Federal do Rio Grande do Norte(UFRN), como exemplo prático de aplicação de conhecimentos técnicos para resolver um problema real e otimizar processos de trabalho.

Desenvolvido com propósito profissional e educacional.
© 2025 - Israel Felipe

