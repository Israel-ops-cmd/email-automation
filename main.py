from dotenv import load_dotenv
import os
import re
import pandas as pd
import fitz  # PyMuPDF
from docx import Document
import smtplib
from email.message import EmailMessage
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading

# Tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Carregar .env
load_dotenv()
remetente = os.getenv('EMAIL_REMETENTE')
senha_app = os.getenv('SENHA_APP')
assunto = os.getenv('ASSUNTO_EMAIL')
corpo_base = os.getenv('CORPO_EMAIL_HTML').replace('\\n', '\n')

# Regex compilados
email_re = re.compile(r'[\w\.-]+@[\w\.-]+', re.IGNORECASE)
cnpj_re = re.compile(r'\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}')
cpf_re = re.compile(r'\d{11}')

# Validações
def validar_nome(nome):
    nome = nome.strip()
    if not nome: return False, "Nome faltando"
    if len(nome) < 2: return False, "Nome muito curto"
    return True, ""

def validar_cnpj(cnpj):
    cnpj = cnpj.strip()
    if not cnpj: return False, "CNPJ faltando"
    if not re.fullmatch(r'[\d./-]+', cnpj): return False, "CNPJ com caracteres inválidos"
    nums = re.sub(r'\D', '', cnpj)
    if len(nums) < 14: return False, "CNPJ incompleto"
    if len(nums) > 14: return False, "CNPJ com dígitos a mais"
    return True, ""

def validar_email(email):
    email = email.strip()
    if not email: return False, "Email faltando"
    if not re.fullmatch(r'[\w\.-]+@[\w\.-]+\.\w{2,}', email, re.IGNORECASE):
        return False, "Email inválido"
    return True, ""

# Extrair dados linha texto
def extrair_dados_linha(linha):
    email = email_re.search(linha)
    cnpj = cnpj_re.search(linha)
    cpf = cpf_re.search(linha)
    email = email.group(0) if email else ''
    cnpj = cnpj.group(0) if cnpj else ''
    linha_limpa = email_re.sub('', linha)
    linha_limpa = cnpj_re.sub('', linha_limpa)
    linha_limpa = cpf_re.sub('', linha_limpa)
    nome = re.sub(r'[-–—]', '', linha_limpa).strip()
    nome = re.sub(r'\s+', ' ', nome)
    return nome, cnpj, email

# Ler arquivos
def ler_docx(path):
    doc = Document(path)
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]

def ler_pdf(path):
    doc = fitz.open(path)
    linhas = []
    for page in doc:
        linhas.extend([l.strip() for l in page.get_text().split('\n') if l.strip()])
    doc.close()
    return linhas

def ler_excel(path):
    df = pd.read_excel(path)
    df.columns = df.columns.str.lower()
    for col in ('nome', 'cnpj', 'email'):
        if col not in df.columns:
            raise ValueError(f"Coluna '{col}' não encontrada no Excel.")
    return [(str(row['nome']).strip(), str(row['cnpj']).strip(), str(row['email']).strip()) for _, row in df.iterrows()]

# Enviar email com HTML
def enviar_email(dest, assunto, corpo_html, remetente, senha):
    msg = EmailMessage()
    msg['From'] = remetente
    msg['To'] = dest
    msg['Subject'] = assunto

    # Fallback em texto simples
    msg.set_content("Este e-mail requer um cliente que suporte HTML.")

    # Corpo em HTML
    msg.add_alternative(corpo_html, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(remetente, senha)
            smtp.send_message(msg)
        return f"✅ Email enviado para {dest}"
    except Exception as e:
        return f"❌ Erro ao enviar para {dest}: {e}"

# Selecionar arquivo (GUI)
def selecionar_arquivo():
    path = filedialog.askopenfilename(title="Selecione o arquivo",
                                      filetypes=[("Arquivos suportados", "*.docx *.xlsx *.xls *.pdf"),
                                                 ("Word", "*.docx"),
                                                 ("Excel", "*.xlsx *.xls"),
                                                 ("PDF", "*.pdf")])
    entry_arquivo.delete(0, ctk.END)
    entry_arquivo.insert(0, path)

# Iniciar envio (processamento)
def iniciar_envio():
    arquivo = entry_arquivo.get()
    if not arquivo:
        messagebox.showerror("Erro", "Selecione um arquivo.")
        return
    ext = os.path.splitext(arquivo)[1].lower()
    try:
        if ext == '.docx':
            linhas = ler_docx(arquivo)
            clientes = [extrair_dados_linha(l) for l in linhas]
        elif ext in ('.xlsx', '.xls'):
            clientes = ler_excel(arquivo)
        elif ext == '.pdf':
            linhas = ler_pdf(arquivo)
            clientes = [extrair_dados_linha(l) for l in linhas]
        else:
            messagebox.showerror("Erro", "Formato de arquivo não suportado.")
            return
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao ler o arquivo:\n{e}")
        return

    clientes_validos = []
    logs = []
    for item in clientes:
        if len(item) == 3:
            nome, cnpj, email = item
        else:
            nome, cnpj, email = '', '', ''

        erros = []
        v_nome, e_nome = validar_nome(nome)
        if not v_nome: erros.append(e_nome)
        v_cnpj, e_cnpj = validar_cnpj(cnpj)
        if not v_cnpj: erros.append(e_cnpj)
        v_email, e_email = validar_email(email)
        if not v_email: erros.append(e_email)

        if erros:
            logs.append(f"⚠️ Cliente ignorado: '{nome}, {cnpj}, {email}': {', '.join(erros)}\n")
        else:
            clientes_validos.append((nome, cnpj, email))

    if not clientes_validos:
        messagebox.showwarning("Aviso", "Nenhum cliente válido encontrado.")
        return

    log_textbox.insert("end", ''.join(logs) + f"\n📊 Total clientes válidos: {len(clientes_validos)}\n\n")
    log_textbox.see("end")

    step = 1 / len(clientes_validos)
    buffer_logs = []
    for idx, (nome, cnpj, email) in enumerate(clientes_validos):
        corpo = corpo_base.format(nome=nome, cnpj=cnpj)
        status = enviar_email(email, assunto, corpo, remetente, senha_app)
        buffer_logs.append(status + '\n')
        progressbar.set((idx + 1) * step)
        if (idx + 1) % 5 == 0 or (idx + 1) == len(clientes_validos):
            log_textbox.insert("end", ''.join(buffer_logs))
            buffer_logs.clear()
            log_textbox.see("end")
            app.update_idletasks()

    messagebox.showinfo("Finalizado", "Envio de emails concluído.")

# GUI
app = ctk.CTk()
app.title("Envio de E-mails Automático")
app.geometry("700x600")
app.resizable(False, False)

label_arquivo = ctk.CTkLabel(app, text="Selecione o arquivo de clientes (.docx, .xlsx, .xls ou .pdf):")
label_arquivo.pack(pady=10)

frame = ctk.CTkFrame(app)
frame.pack(pady=5)

entry_arquivo = ctk.CTkEntry(frame, width=450)
entry_arquivo.pack(side="left", padx=5)

btn_procurar = ctk.CTkButton(frame, text="Procurar", command=selecionar_arquivo)
btn_procurar.pack(side="left", padx=5)

btn_enviar = ctk.CTkButton(app, text="Enviar E-mails", command=lambda: threading.Thread(target=iniciar_envio).start(), fg_color="green", hover_color="#006400")
btn_enviar.pack(pady=15)

progressbar = ctk.CTkProgressBar(app, width=600)
progressbar.set(0)
progressbar.pack(pady=10)

log_textbox = ctk.CTkTextbox(app, width=650, height=350)
log_textbox.pack(padx=10, pady=10)

app.mainloop()
