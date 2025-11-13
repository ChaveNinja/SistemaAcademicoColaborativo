import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ---------------- VARIÁVEL DE PERFIL ----------------
perfil_usuario = None  # será definido após login

# ---------------- FUNÇÕES AUXILIARES ----------------


def caminhos():
    pasta = os.path.dirname(os.path.abspath(__file__))
    caminho_turmas = os.path.join(pasta, "output", "output", "turmas.txt")
    caminho_alunos = os.path.join(pasta, "output", "output", "alunos.txt")
    pasta_individual = os.path.join(
        pasta, "output", "output", "dados", "alunos")
    return caminho_turmas, caminho_alunos, pasta_individual

# ---------------- LOGIN ----------------


def login():
    global perfil_usuario
    login_win = tk.Toplevel()
    login_win.title("Login")
    login_win.geometry("300x150")
    login_win.grab_set()

    tk.Label(login_win, text="Usuário:").pack(pady=5)
    entry_user = tk.Entry(login_win)
    entry_user.pack()

    tk.Label(login_win, text="Senha:").pack(pady=5)
    entry_pass = tk.Entry(login_win, show="*")
    entry_pass.pack()

    def verificar_login():
        global perfil_usuario
        user = entry_user.get().strip().lower()
        senha = entry_pass.get().strip().lower()

        if (user == "aluno" and senha == "aluno"):
            perfil_usuario = "aluno"
        elif (user == "professor" and senha == "professor"):
            perfil_usuario = "professor"
        elif (user == "diretor" and senha == "diretor"):
            perfil_usuario = "diretor"
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos")
            return

        messagebox.showinfo(
            "Login", f"Bem-vindo {perfil_usuario.capitalize()}!")

        # Ajuste das permissões
        if perfil_usuario == "aluno":
            # Campos bloqueados
            for e in [entry_numgrupo, entry_grupo, entry_matricula, entry_nome, entry_np1, entry_np2, entry_pim]:
                e.config(state="disabled")
            # Botões bloqueados
            btn_salvar.config(state="disabled")
            btn_remover.config(state="disabled")
            btn_adicionar.config(state="disabled")

        elif perfil_usuario == "professor":
            # Somente campos de notas habilitados
            for e in [entry_np1, entry_np2, entry_pim]:
                e.config(state="normal")
            for e in [entry_numgrupo, entry_grupo, entry_matricula, entry_nome]:
                e.config(state="disabled")
            # Botões
            btn_salvar.config(state="normal")
            btn_remover.config(state="disabled")
            btn_adicionar.config(state="disabled")

        elif perfil_usuario == "diretor":
            # Todos campos habilitados
            for e in [entry_numgrupo, entry_grupo, entry_matricula, entry_nome, entry_np1, entry_np2, entry_pim]:
                e.config(state="normal")
            # Todos botões habilitados
            btn_salvar.config(state="normal")
            btn_remover.config(state="normal")
            btn_adicionar.config(state="normal")

        login_win.destroy()

    tk.Button(login_win, text="Entrar", command=verificar_login).pack(pady=10)

# ---------------- CARREGAR DADOS ----------------


def carregar_dados():
    caminho_turmas, caminho_alunos, _ = caminhos()

    if not os.path.exists(caminho_turmas) or not os.path.exists(caminho_alunos):
        messagebox.showerror(
            "Erro", "Execute os programas em C para gerar os arquivos primeiro.")
        return

    tree.delete(*tree.get_children())
    turmas = {}
    with open(caminho_turmas, "r", encoding="utf-8") as t:
        for linha in t.readlines():
            partes = linha.strip().split(",")
            if len(partes) == 2:
                turmas[int(partes[0])] = partes[1]

    with open(caminho_alunos, "r", encoding="utf-8") as a:
        for linha in a:
            dados = linha.strip().split(",")
            if len(dados) == 7:
                cod_turma, matricula, nome, np1, np2, pim, media = dados
                media = float(media)
                situacao = "APROVADO" if media >= 7 else "REPROVADO"
                turma_nome = turmas.get(int(cod_turma), "Não encontrada")
                tree.insert(
                    "", tk.END,
                    values=(cod_turma, turma_nome, matricula, nome,
                            np1, np2, pim, f"{media:.2f}", situacao),
                    tags=("aprovado" if media >= 7 else "reprovado",)
                )

    tree.tag_configure("aprovado", background="#c6efce")
    tree.tag_configure("reprovado", background="#ffc7ce")

# ---------------- SELECIONAR ALUNO ----------------


def selecionar_aluno(event):
    selecionado = tree.selection()
    if not selecionado:
        return
    item = tree.item(selecionado[0])
    valores = item["values"]

    for entry, val in zip([entry_numgrupo, entry_grupo, entry_matricula, entry_nome, entry_np1, entry_np2, entry_pim], valores[:7]):
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, val)
        # Reaplica estado de permissão
        if perfil_usuario == "aluno":
            entry.config(state="disabled")
        elif perfil_usuario == "professor":
            if entry not in [entry_np1, entry_np2, entry_pim]:
                entry.config(state="disabled")

# ---------------- SALVAR ALTERAÇÃO ----------------


def salvar_alteracao():
    if perfil_usuario == "aluno":
        messagebox.showwarning("Atenção", "Aluno não pode alterar notas.")
        return

    selecionado = tree.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um aluno para alterar.")
        return

    try:
        np1 = float(entry_np1.get())
        np2 = float(entry_np2.get())
        pim = float(entry_pim.get())
    except ValueError:
        messagebox.showerror("Erro", "As notas devem ser números válidos.")
        return

    caminho_turmas, caminho_alunos, pasta_individual = caminhos()
    novo_num_grupo = entry_numgrupo.get().strip()
    novo_grupo_nome = entry_grupo.get().strip()
    nova_matricula = entry_matricula.get().strip()
    novo_nome = entry_nome.get().strip()

    item = tree.item(selecionado[0])
    nome_antigo = item["values"][3]

    with open(caminho_alunos, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    media = round(np1 * 0.4 + np2 * 0.4 + pim * 0.2, 2)
    nova_linha = f"{novo_num_grupo},{nova_matricula},{novo_nome},{np1},{np2},{pim},{media}\n"

    alterado = False
    for i, linha in enumerate(linhas):
        dados = linha.strip().split(",")
        if len(dados) == 7 and dados[2] == nome_antigo:
            linhas[i] = nova_linha
            alterado = True
            break

    if alterado:
        with open(caminho_alunos, "w", encoding="utf-8") as f:
            f.writelines(linhas)

        situacao = "APROVADO" if media >= 7 else "REPROVADO"
        tree.item(selecionado[0], values=(novo_num_grupo, novo_grupo_nome,
                  nova_matricula, novo_nome, np1, np2, pim, f"{media:.2f}", situacao))
        tree.item(selecionado[0], tags=(
            "aprovado" if media >= 7 else "reprovado",))
        messagebox.showinfo(
            "Sucesso", f"O aluno '{nome_antigo}' foi atualizado para '{novo_nome}' com sucesso.")
    else:
        messagebox.showwarning("Atenção", "Aluno não encontrado no arquivo.")

# ---------------- REMOVER ALUNO ----------------


def remover_aluno():
    if perfil_usuario != "diretor":
        messagebox.showwarning(
            "Atenção", "Apenas o Diretor pode remover alunos.")
        return

    selecionado = tree.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um aluno para remover.")
        return

    item = tree.item(selecionado[0])
    nome = item["values"][3]

    resposta = messagebox.askyesno(
        "Confirmar Exclusão", f"Tem certeza que deseja remover o aluno '{nome}'?")
    if not resposta:
        return

    caminho_turmas, caminho_alunos, pasta_individual = caminhos()

    with open(caminho_alunos, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    novas_linhas = [linha for linha in linhas if nome not in linha]

    with open(caminho_alunos, "w", encoding="utf-8") as f:
        f.writelines(novas_linhas)

    tree.delete(selecionado[0])
    messagebox.showinfo(
        "Removido", f"O aluno '{nome}' foi removido com sucesso.")

# ---------------- ADICIONAR ALUNO ----------------


def adicionar_aluno():
    if perfil_usuario != "diretor":
        messagebox.showwarning(
            "Atenção", "Apenas o Diretor pode adicionar alunos.")
        return

    caminho_turmas, caminho_alunos, _ = caminhos()

    matricula = simpledialog.askstring(
        "Matrícula", "Digite a matrícula do aluno:")
    if not matricula:
        return
    nome = simpledialog.askstring("Nome", "Digite o nome do aluno:")
    if not nome:
        return
    num_grupo = simpledialog.askstring(
        "Número do Grupo", "Digite o número do grupo:")
    if not num_grupo:
        return

    np1, np2, pim, media = 0.0, 0.0, 0.0, 0.0
    nova_linha = f"{num_grupo},{matricula},{nome},{np1},{np2},{pim},{media}\n"
    with open(caminho_alunos, "a", encoding="utf-8") as f:
        f.write(nova_linha)

    carregar_dados()
    messagebox.showinfo("Sucesso", f"Aluno '{nome}' adicionado com sucesso.")


# ---------------- INTERFACE ----------------
janela = tk.Tk()
janela.title("Sistema Escolar - Gestão de Turmas e Alunos")
janela.geometry("1200x600")
janela.configure(bg="#f0f0f0")

# Botão de login
tk.Button(janela, text="Login", command=login, bg="#0078D7",
          fg="white", font=("Arial", 11, "bold")).pack(pady=10)

# Título
tk.Label(janela, text="Gestão de Turmas e Alunos", font=(
    "Arial", 16, "bold"), bg="#f0f0f0").pack(pady=5)

# Treeview
colunas = ("Número do Grupo", "Turma", "Matrícula", "Aluno",
           "NP1", "NP2", "PIM", "Média", "Situação")
tree = ttk.Treeview(janela, columns=colunas, show="headings")
for col in colunas:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=120)
tree.pack(expand=True, fill="both", pady=10)
tree.bind("<<TreeviewSelect>>", selecionar_aluno)

# Campos de edição
frame_edicao = tk.Frame(janela, bg="#f0f0f0")
frame_edicao.pack(pady=10)
tk.Label(frame_edicao, text="Número do Grupo:",
         bg="#f0f0f0").grid(row=0, column=0, padx=5)
entry_numgrupo = tk.Entry(frame_edicao, width=10)
entry_numgrupo.grid(row=0, column=1, padx=5)
tk.Label(frame_edicao, text="Nome da Turma:",
         bg="#f0f0f0").grid(row=0, column=2, padx=5)
entry_grupo = tk.Entry(frame_edicao, width=20)
entry_grupo.grid(row=0, column=3, padx=5)
tk.Label(frame_edicao, text="Matrícula:",
         bg="#f0f0f0").grid(row=0, column=4, padx=5)
entry_matricula = tk.Entry(frame_edicao, width=15)
entry_matricula.grid(row=0, column=5, padx=5)
tk.Label(frame_edicao, text="Aluno:", bg="#f0f0f0").grid(
    row=0, column=6, padx=5)
entry_nome = tk.Entry(frame_edicao, width=20)
entry_nome.grid(row=0, column=7, padx=5)
tk.Label(frame_edicao, text="NP1:", bg="#f0f0f0").grid(row=0, column=8, padx=5)
entry_np1 = tk.Entry(frame_edicao, width=6)
entry_np1.grid(row=0, column=9, padx=5)
tk.Label(frame_edicao, text="NP2:", bg="#f0f0f0").grid(
    row=0, column=10, padx=5)
entry_np2 = tk.Entry(frame_edicao, width=6)
entry_np2.grid(row=0, column=11, padx=5)
tk.Label(frame_edicao, text="PIM:", bg="#f0f0f0").grid(
    row=0, column=12, padx=5)
entry_pim = tk.Entry(frame_edicao, width=6)
entry_pim.grid(row=0, column=13, padx=5)

# Botões principais
frame_botoes = tk.Frame(janela, bg="#f0f0f0")
frame_botoes.pack(pady=5)
btn_carregar = tk.Button(frame_botoes, text="Carregar Dados", command=carregar_dados,
                         bg="#0078D7", fg="white", font=("Arial", 11, "bold"), width=15)
btn_carregar.grid(row=0, column=0, padx=10)
btn_salvar = tk.Button(frame_botoes, text="Salvar Alteração", command=salvar_alteracao,
                       bg="#28a745", fg="white", font=("Arial", 11, "bold"), width=15)
btn_salvar.grid(row=0, column=1, padx=10)
btn_remover = tk.Button(frame_botoes, text="Remover Aluno", command=remover_aluno,
                        bg="#dc3545", fg="white", font=("Arial", 11, "bold"), width=15)
btn_remover.grid(row=0, column=2, padx=10)
btn_adicionar = tk.Button(frame_botoes, text="Adicionar Aluno", command=adicionar_aluno,
                          bg="#ffc107", fg="black", font=("Arial", 11, "bold"), width=15)
btn_adicionar.grid(row=0, column=3, padx=10)

# Mensagem
msg = tk.Label(janela, text="Selecione um aluno para alterar dados ou remover do sistema.",
               bg="#f0f0f0", fg="#333", font=("Arial", 10))
msg.pack(pady=5)

janela.mainloop()
