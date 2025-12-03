import tkinter as tk
from tkinter import messagebox
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime


# -----------------------------------
# Conexão com MySQL no Docker
# -----------------------------------
def conectar():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="1234",
        database="sistema_login"
    )

# -----------------------------------
# Função para carregar produtos
# -----------------------------------
def carregar_produtos(listbox):
    listbox.delete(0, tk.END)

    con = conectar()
    cursor = con.cursor()
    cursor.execute("SELECT produto, quantidade, valor FROM produtos")
    dados = cursor.fetchall()
    con.close()

    # Cabeçalho alinhado
    cabecalho = f"{'Produto'.ljust(20)} {'Qtd'.ljust(8)} {'Valor (R$)'.ljust(10)}"
    listbox.insert(tk.END, cabecalho)
    listbox.insert(tk.END, "-" * 45)

    # Conteúdo
    for prod, qtd, val in dados:
        linha = f"{prod.ljust(20)} {str(qtd).ljust(8)} {str(val).ljust(10)}"
        listbox.insert(tk.END, linha)


def limpar_listbox():
    listbox_produtos.delete(0, tk.END)



def gerar_relatorio(lista):
    # Nome do arquivo PDF com data/hora
    nome_pdf = f"relatorio_produtos_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"

    # Criando o PDF
    c = canvas.Canvas(nome_pdf, pagesize=letter)
    largura, altura = letter

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, altura - 50, "Relatório de Produtos")

    # Cabeçalho
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, altura - 90, "Produto")
    c.drawString(250, altura - 90, "Quantidade")
    c.drawString(350, altura - 90, "Valor (R$)")

    # Linha inicial dos dados
    y = altura - 110

    c.setFont("Helvetica", 11)

    # Começar a partir da terceira linha (porque as duas primeiras são cabeçalho)
    for i in range(2, lista.size()):
        linha = lista.get(i)
        partes = linha.split()

        try:
            produto = partes[0]
            quantidade = partes[-3]   # "Qtd: X"
            valor = partes[-1]        # "R$: Y"

            # Escrever no PDF
            c.drawString(40, y, produto)
            c.drawString(250, y, quantidade.replace("Qtd:", ""))
            c.drawString(350, y, valor.replace("R$:", ""))

            y -= 20

            # Quebra de página automática
            if y < 40:
                c.showPage()
                y = altura - 50

        except:
            pass

    # Finaliza o PDF
    c.save()

    messagebox.showinfo("Relatório Gerado", f"Relatório salvo como:\n{nome_pdf}")


# -----------------------------------
# Tela de Cadastro de Produtos
# -----------------------------------
def tela_produtos():
    janela_produtos = tk.Tk()
    janela_produtos.title("Cadastro de Produtos")
    janela_produtos.geometry("1200x750+0+0")

    # Label e entradas
    tk.Label(janela_produtos, text="Produto:").grid(row=0, column=0, padx=10, pady=5)
    entry_produto = tk.Entry(janela_produtos)
    entry_produto.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(janela_produtos, text="Quantidade:").grid(row=1, column=0, padx=10, pady=5)
    entry_quantidade = tk.Entry(janela_produtos)
    entry_quantidade.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(janela_produtos, text="Valor Unitário:").grid(row=2, column=0, padx=10, pady=5)
    entry_valor = tk.Entry(janela_produtos)
    entry_valor.grid(row=2, column=1, padx=10, pady=5)

    # Listbox para mostrar produtos
    lista = tk.Listbox(janela_produtos, width=60, selectmode=tk.SINGLE,font=("Courier", 12))
    lista.grid(row=0, column=3, rowspan=6, padx=40)

    carregar_produtos(lista)

    # Função para registrar produto
    def registrar_produto():
        produto = entry_produto.get()
        quantidade = entry_quantidade.get()
        valor = entry_valor.get()

        if produto == "" or quantidade == "" or valor == "":
            messagebox.showwarning("Atenção", "Preencha todos os campos!")
            return

        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO produtos (produto, quantidade, valor) VALUES (%s, %s, %s)",
                (produto, quantidade, valor)
            )
            con.commit()
            con.close()

            # Limpar campos
            entry_produto.delete(0, tk.END)
            entry_quantidade.delete(0, tk.END)
            entry_valor.delete(0, tk.END)

            # Atualizar lista
            carregar_produtos(lista)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar produto:\n{e}")


    def deletar_produto():
        selecionado = lista.curselection()

        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto para deletar!")
            return

        linha = lista.get(selecionado)

        # Ignorar cabeçalho
        if "Produto" in linha or "---" in linha:
            messagebox.showwarning("Atenção", "Selecione uma linha válida (produto)!")
            return

        # Produto está no início da linha (antes do espaço)
        produto_nome = linha.split()[0]

        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute("DELETE FROM produtos WHERE produto=%s", (produto_nome,))
            con.commit()
            con.close()

            carregar_produtos(lista)
            messagebox.showinfo("Sucesso", "Produto deletado!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao deletar:\n{e}")


    def deletar_todos_produtos():
        resposta = messagebox.askyesno(
            "Confirmar",
            "Tem certeza que deseja apagar TODOS os produtos?"
        )

        if resposta:
            try:
                con = conectar()
                cursor = con.cursor()
                cursor.execute("DELETE FROM produtos")
                con.commit()
                con.close()

                carregar_produtos(lista)
                messagebox.showinfo("Sucesso", "Todos os produtos foram apagados!")

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao apagar produtos:\n{e}")



    # Botão Registrar
    tk.Button(janela_produtos, text="Registrar Produto", command=registrar_produto).grid(
        row=3, column=1, pady=20
    )
    tk.Button(janela_produtos, text="Gerar Relatório", command=lambda: gerar_relatorio(lista)).grid(
    row=6, column=3, pady=10
    )
    tk.Button(janela_produtos, text="Deletar Produto", command=deletar_produto, bg="red", fg="white").grid(
    row=4, column=1, pady=10
    )
    tk.Button(
        janela_produtos,
        text="Limpar TODOS os Produtos",
        command=deletar_todos_produtos,
        bg="darkred",
        fg="white"
        ).grid(row=5, column=1, pady=10)



    janela_produtos.mainloop()

# -----------------------------------
# Função Login
# -----------------------------------
def login():
    user = entry_user.get()
    senha = entry_senha.get()

    if user == "" or senha == "":
        messagebox.showwarning("Atenção", "Preencha todos os campos!")
        return

    con = conectar()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username=%s AND senha=%s", (user, senha))
    resultado = cursor.fetchone()
    con.close()

    if resultado:
        janela.destroy()  # FECHA a tela de login
        tela_produtos()   # Abre nova tela
    else:
        messagebox.showerror("Erro", "Usuário ou senha incorretos.")

# -----------------------------------
# Função Registrar Usuário
# -----------------------------------
def registrar():
    user = entry_user.get()
    senha = entry_senha.get()

    if user == "" or senha == "":
        messagebox.showwarning("Atenção", "Preencha todos os campos!")
        return

    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute("INSERT INTO usuarios (username, senha) VALUES (%s, %s)", (user, senha))
        con.commit()
        con.close()
        messagebox.showinfo("Sucesso", "Usuário registrado!")

    except mysql.connector.IntegrityError:
        messagebox.showwarning("Atenção", "Usuário já existe!")

# -----------------------------------
# Interface Tkinter — Tela Login
# -----------------------------------
janela = tk.Tk()
janela.title("Login")
janela.geometry("300x230+0+0")


tk.Label(janela, text="Login / Registro", font=("Arial", 14)).pack(pady=10)

tk.Label(janela, text="Usuário:").pack()
entry_user = tk.Entry(janela)
entry_user.pack()

tk.Label(janela, text="Senha:").pack()
entry_senha = tk.Entry(janela, show="*")
entry_senha.pack()

tk.Button(janela, text="Entrar", width=15, command=login).pack(pady=10)
tk.Button(janela, text="Registrar", width=15, command=registrar).pack()

janela.mainloop()
