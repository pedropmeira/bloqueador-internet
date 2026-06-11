import os
import tempfile
import ctypes
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

# ── Paleta ─────────────────────────────────────────────────────────────────────
C_HEADER     = '#0d1117'
C_HEADER_SUB = '#161b22'
C_BG         = '#f6f8fa'
C_CARD       = '#ffffff'
C_BORDA      = '#d0d7de'
C_AZUL       = '#0969da'
C_VERDE      = '#1a7f37'
C_VERMELHO   = '#cf222e'
C_LARANJA    = '#bc4c00'
C_TEXTO      = '#1f2328'
C_MUTED      = '#656d76'
C_RODAPE     = '#0d1117'
C_ACCENT     = '#ddf4ff'

EXTENSOES_EXE = {'.exe', '.msi', '.bat', '.cmd', '.com', '.ps1', '.vbs', '.sh'}
executaveis_encontrados = []
regras_meta = {}  # item_id -> display_name (tab2)

# ── Helpers ────────────────────────────────────────────────────────────────────
def set_status(msg, erro=False):
    status_var.set(msg)
    status_label.config(fg='#cf222e' if erro else C_MUTED)

def rodar_como_admin(script_ps):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.ps1', mode='w', encoding='utf-8')
    tmp.write(script_ps)
    tmp.close()
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", "powershell.exe",
        f'-NoProfile -ExecutionPolicy Bypass -File "{tmp.name}"',
        None, 1
    )

# ── Tab 1: Buscar e Bloquear ───────────────────────────────────────────────────
def selecionar_pasta():
    pasta = filedialog.askdirectory(title="Selecione uma pasta")
    if pasta:
        entrada_pasta.set(os.path.normpath(pasta))

def buscar_executaveis():
    global executaveis_encontrados
    pasta = entrada_pasta.get()
    if not pasta or not os.path.isdir(pasta):
        set_status("Selecione uma pasta válida.", erro=True)
        return

    for row in lista_resultado.get_children():
        lista_resultado.delete(row)
    caminho_texto.config(state='normal')
    caminho_texto.delete('1.0', tk.END)
    set_status("Buscando executáveis...")
    btn_buscar.config(state='disabled', text="Buscando...")
    janela.update()

    executaveis_encontrados = []
    try:
        for raiz, dirs, arquivos in os.walk(pasta):
            for arquivo in arquivos:
                _, ext = os.path.splitext(arquivo)
                if ext.lower() in EXTENSOES_EXE:
                    caminho_completo = os.path.normpath(os.path.join(raiz, arquivo))
                    executaveis_encontrados.append((arquivo, caminho_completo))
    finally:
        btn_buscar.config(state='normal', text="Procurar")

    for nome, caminho in executaveis_encontrados:
        lista_resultado.insert('', 'end', values=(nome, caminho))

    if executaveis_encontrados:
        linhas = [f'    "{c}",' for _, c in executaveis_encontrados]
        linhas[-1] = linhas[-1].rstrip(',')
        caminho_texto.insert('1.0', '\n'.join(linhas))
        btn_bloquear.config(state='normal')
        set_status(f"{len(executaveis_encontrados)} executável(is) encontrado(s).")
    else:
        caminho_texto.insert('1.0', "Nenhum executável encontrado.")
        btn_bloquear.config(state='disabled')
        set_status("Nenhum executável encontrado.", erro=True)

    caminho_texto.config(state='disabled')

def executar_script(script_ps, win):
    win.destroy()
    try:
        rodar_como_admin(script_ps)
        set_status("Script enviado ao PowerShell como Administrador.")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível executar como administrador:\n{e}")

def aplicar_bloqueio():
    if not executaveis_encontrados:
        return

    bloquear_entrada = var_inbound.get()
    entradas = '\n'.join(f'    "{c}",' for _, c in executaveis_encontrados)
    entradas = entradas.rstrip(',')

    bloco_inbound = ""
    if bloquear_entrada:
        bloco_inbound = """
        New-NetFirewallRule `
            -DisplayName "Bloqueio de Internet para $program" `
            -Direction Inbound `
            -Program $program `
            -Action Block `
            -Profile Any
        Write-Output "  [Entrada] Regra criada para: $program"
"""

    script_ps = f"""$programs = @(
{entradas}
)

foreach ($program in $programs) {{
    if (Test-Path $program) {{
        New-NetFirewallRule `
            -DisplayName "Bloqueio de Internet para $program" `
            -Direction Outbound `
            -Program $program `
            -Action Block `
            -Profile Any
        Write-Output "  [Saida] Regra criada para: $program"{bloco_inbound}
    }} else {{
        Write-Output "  [AVISO] Nao encontrado: $program"
    }}
}}

Write-Output ""
Write-Output "--- Concluido. Pressione Enter para fechar ---"
Read-Host
"""

    preview = tk.Toplevel(janela)
    preview.title("Prévia — Script PowerShell")
    preview.geometry("860x560")
    preview.configure(bg=C_BG)
    preview.grab_set()
    preview.resizable(True, True)

    hdr = tk.Frame(preview, bg=C_HEADER, height=52)
    hdr.pack(fill='x')
    hdr.pack_propagate(False)
    tk.Label(hdr, text="Revisão do Script", font=('Segoe UI', 13, 'bold'),
             bg=C_HEADER, fg='white').pack(side='left', padx=16, pady=12)
    tk.Label(hdr, text=f"  {len(executaveis_encontrados)} programa(s)  ",
             font=('Segoe UI', 9), bg='#388bfd', fg='white').pack(side='left', pady=14)
    if bloquear_entrada:
        tk.Label(hdr, text="  Entrada + Saída  ",
                 font=('Segoe UI', 9), bg=C_LARANJA, fg='white').pack(side='left', padx=6, pady=14)

    tk.Label(preview,
             text="O script abaixo será executado no PowerShell como Administrador. Revise antes de confirmar.",
             font=('Segoe UI', 9), bg=C_BG, fg=C_MUTED).pack(anchor='w', padx=16, pady=(10, 4))

    frame_sc = tk.Frame(preview, bg=C_BG, padx=16)
    frame_sc.pack(fill='both', expand=True, pady=(0, 6))
    sy = tk.Scrollbar(frame_sc); sy.pack(side='right', fill='y')
    sx = tk.Scrollbar(frame_sc, orient='horizontal'); sx.pack(side='bottom', fill='x')
    caixa = tk.Text(frame_sc, font=('Courier New', 9), bg='#0d1117', fg='#e6edf3',
                    wrap='none', relief='flat', bd=0,
                    yscrollcommand=sy.set, xscrollcommand=sx.set)
    caixa.insert('1.0', script_ps.strip())
    caixa.config(state='disabled')
    caixa.pack(fill='both', expand=True)
    sy.config(command=caixa.yview); sx.config(command=caixa.xview)

    rp = tk.Frame(preview, bg=C_BG, pady=10); rp.pack(fill='x', padx=16)
    tk.Button(rp, text="Cancelar", command=preview.destroy,
              font=('Segoe UI', 10), bg=C_CARD, fg=C_TEXTO,
              relief='solid', bd=1, padx=18, pady=6, cursor='hand2').pack(side='right', padx=(8, 0))
    tk.Button(rp, text="  Confirmar e Executar  ",
              command=lambda: executar_script(script_ps, preview),
              font=('Segoe UI', 10, 'bold'), bg=C_VERMELHO, fg='white',
              relief='flat', bd=0, padx=18, pady=6, cursor='hand2').pack(side='right')

# ── Tab 2: Gerenciar Bloqueios ─────────────────────────────────────────────────
def processar_regras(linhas):
    grupos = {}
    for linha in linhas:
        partes = linha.split('|', 2)
        if len(partes) < 3:
            continue
        direcao, display_name, programa = partes[0].strip(), partes[1].strip(), partes[2].strip()
        pasta_prog = os.path.dirname(programa) if programa != 'Desconhecido' else 'Desconhecido'
        grupos.setdefault(pasta_prog, []).append((direcao, display_name, programa))

    for pasta_prog, regras in sorted(grupos.items()):
        nome_grupo = os.path.basename(pasta_prog) or pasta_prog
        gid = arvore_regras.insert('', 'end',
                                   text=f"  {nome_grupo}",
                                   values=('', f"{len(regras)} regra(s)", pasta_prog),
                                   open=True, tags=('grupo',))
        for direcao, display_name, programa in regras:
            dir_label = 'Saída' if 'Outbound' in direcao else 'Entrada'
            tag_dir   = 'outbound' if 'Outbound' in direcao else 'inbound'
            iid = arvore_regras.insert(gid, 'end',
                                       text='',
                                       values=(os.path.basename(programa), dir_label, programa),
                                       tags=(tag_dir,))
            regras_meta[iid] = display_name

    total = sum(len(r) for r in grupos.values())
    if total:
        set_status(f"{total} regra(s) de bloqueio ativa(s).")
    else:
        set_status("Nenhuma regra de bloqueio encontrada.", erro=True)
    btn_atualizar.config(state='normal', text="Atualizar Lista")

def carregar_regras():
    global regras_meta
    regras_meta = {}
    btn_atualizar.config(state='disabled', text="Aguardando admin...")
    for item in arvore_regras.get_children():
        arvore_regras.delete(item)
    set_status("Aguardando permissão de administrador para ler o firewall...")
    janela.update()

    out_path  = os.path.join(tempfile.gettempdir(), 'praxedes_fw_out.txt')
    done_path = os.path.join(tempfile.gettempdir(), 'praxedes_fw_done.txt')
    for p in [out_path, done_path]:
        try: os.unlink(p)
        except: pass

    script = (
        '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n'
        f'$out = "{out_path}"\n'
        '$rules = Get-NetFirewallRule | Where-Object { $_.DisplayName -like "Bloqueio de Internet para *" }\n'
        'foreach ($r in $rules) {\n'
        '    try { $app = ($r | Get-NetFirewallApplicationFilter).Program }\n'
        '    catch { $app = "Desconhecido" }\n'
        '    Add-Content -Path $out -Value "$($r.Direction)|$($r.DisplayName)|$app" -Encoding UTF8\n'
        '}\n'
        f'Set-Content -Path "{done_path}" -Value "done" -Encoding UTF8\n'
    )

    tmp_ps = tempfile.NamedTemporaryFile(delete=False, suffix='.ps1', mode='w', encoding='utf-8')
    tmp_ps.write(script)
    tmp_ps.close()

    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", "powershell.exe",
        f'-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{tmp_ps.name}"',
        None, 0
    )

    def poll(tentativas=0):
        if tentativas > 40:
            set_status("Tempo esgotado ou UAC foi cancelado.", erro=True)
            btn_atualizar.config(state='normal', text="Atualizar Lista")
            return

        if os.path.exists(done_path):
            try:
                with open(out_path, 'r', encoding='utf-8', errors='replace') as f:
                    linhas = [l.strip() for l in f.read().splitlines() if '|' in l]
            except Exception:
                linhas = []
            processar_regras(linhas)
            for p in [out_path, done_path, tmp_ps.name]:
                try: os.unlink(p)
                except: pass
            return

        janela.after(500, lambda: poll(tentativas + 1))

    janela.after(800, poll)


def desbloquear_selecionado():
    sel = arvore_regras.selection()
    if not sel:
        messagebox.showwarning("Aviso", "Selecione ao menos uma regra para desbloquear.")
        return

    display_names = []
    for item in sel:
        if item in regras_meta:
            display_names.append(regras_meta[item])
        else:
            for filho in arvore_regras.get_children(item):
                if filho in regras_meta:
                    display_names.append(regras_meta[filho])

    if not display_names:
        return

    ok = messagebox.askokcancel(
        "Atenção — Desbloquear Internet",
        f"Você está prestes a REMOVER {len(display_names)} regra(s) de bloqueio.\n\n"
        "Os programas selecionados voltarão a ter acesso à internet.\n\n"
        "Deseja continuar?",
        icon='warning'
    )
    if not ok:
        return

    linhas_remove = '\n'.join(
        f'Remove-NetFirewallRule -DisplayName "{dn}"; Write-Output "Removido: {dn}"'
        for dn in display_names
    )
    script_ps = f"""{linhas_remove}

Write-Output ""
Write-Output "{len(display_names)} regra(s) removida(s) com sucesso."
Write-Output "--- Pressione Enter para fechar ---"
Read-Host
"""
    try:
        rodar_como_admin(script_ps)
        set_status(f"Remoção de {len(display_names)} regra(s) enviada como Administrador.")
        janela.after(4000, carregar_regras)
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível executar como administrador:\n{e}")

# ── Janela principal ───────────────────────────────────────────────────────────
janela = tk.Tk()
janela.title("Bloqueador de Internet — Praxedes")
janela.configure(bg=C_BG)
janela.resizable(True, True)
janela.minsize(780, 560)
janela.state('zoomed')

try:
    janela.iconbitmap(default='icon.ico')
except Exception:
    pass

header = tk.Frame(janela, bg=C_HEADER, height=64)
header.pack(fill='x')
header.pack_propagate(False)
tk.Label(header, text="Bloqueador de Internet", font=('Segoe UI', 16, 'bold'),
         bg=C_HEADER, fg='white').pack(side='left', padx=20, pady=14)
tk.Label(header, text="by Praxedes", font=('Segoe UI', 9),
         bg=C_HEADER, fg='#8b949e').pack(side='left', pady=20)
tk.Label(header, text="Firewall Manager", font=('Segoe UI', 9),
         bg='#21262d', fg='#58a6ff', padx=10, pady=4).pack(side='right', padx=20, pady=18)
tk.Frame(janela, bg=C_HEADER_SUB, height=3).pack(fill='x')

style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook', background=C_BG, borderwidth=0)
style.configure('TNotebook.Tab', font=('Segoe UI', 10), padding=[18, 7],
                background='#e1e4e8', foreground=C_MUTED)
style.map('TNotebook.Tab',
          background=[('selected', C_CARD)],
          foreground=[('selected', C_TEXTO)])
style.configure('Prax.Treeview', background=C_CARD, foreground=C_TEXTO,
                fieldbackground=C_CARD, rowheight=26, font=('Segoe UI', 9))
style.configure('Prax.Treeview.Heading', background=C_HEADER_SUB, foreground='white',
                font=('Segoe UI', 9, 'bold'), relief='flat')
style.map('Prax.Treeview', background=[('selected', C_ACCENT)],
          foreground=[('selected', C_AZUL)])
style.configure('Gerenciar.Treeview', background=C_CARD, foreground=C_TEXTO,
                fieldbackground=C_CARD, rowheight=28, font=('Segoe UI', 9))
style.configure('Gerenciar.Treeview.Heading', background=C_HEADER_SUB, foreground='white',
                font=('Segoe UI', 9, 'bold'), relief='flat')
style.map('Gerenciar.Treeview', background=[('selected', '#fff0f0')],
          foreground=[('selected', C_VERMELHO)])

notebook = ttk.Notebook(janela)
notebook.pack(fill='both', expand=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Buscar e Bloquear
# ══════════════════════════════════════════════════════════════════════════════
tab1 = tk.Frame(notebook, bg=C_BG)
notebook.add(tab1, text="  Buscar e Bloquear  ")

card_sel = tk.Frame(tab1, bg=C_CARD, highlightbackground=C_BORDA, highlightthickness=1)
card_sel.pack(fill='x', padx=20, pady=(16, 0))
inner = tk.Frame(card_sel, bg=C_CARD, pady=12, padx=16)
inner.pack(fill='x')

tk.Label(inner, text="Pasta de origem", font=('Segoe UI', 10, 'bold'),
         bg=C_CARD, fg=C_TEXTO).grid(row=0, column=0, sticky='w', columnspan=3)

entrada_pasta = tk.StringVar()
tk.Entry(inner, textvariable=entrada_pasta, font=('Segoe UI', 10),
         bg='#f6f8fa', fg=C_TEXTO, relief='solid', bd=1).grid(
    row=1, column=0, sticky='ew', padx=(0, 8), pady=(6, 0), ipady=5)
tk.Button(inner, text="Selecionar Pasta", command=selecionar_pasta,
          font=('Segoe UI', 10), bg=C_AZUL, fg='white',
          relief='flat', padx=14, pady=5, cursor='hand2').grid(row=1, column=1, pady=(6, 0))
btn_buscar = tk.Button(inner, text="Procurar", command=buscar_executaveis,
                       font=('Segoe UI', 10, 'bold'), bg=C_VERDE, fg='white',
                       relief='flat', padx=20, pady=5, cursor='hand2')
btn_buscar.grid(row=1, column=2, padx=(8, 0), pady=(6, 0))
inner.columnconfigure(0, weight=1)

frame_chk = tk.Frame(card_sel, bg=C_CARD, padx=16, pady=6)
frame_chk.pack(fill='x')
var_inbound = tk.BooleanVar(value=False)
tk.Checkbutton(frame_chk,
               text="Bloquear também a entrada de internet (Inbound)",
               variable=var_inbound, font=('Segoe UI', 9),
               bg=C_CARD, fg=C_TEXTO, activebackground=C_CARD,
               selectcolor=C_CARD, cursor='hand2').pack(side='left')
tk.Label(frame_chk, text="  Bloqueia conexões recebidas além das enviadas",
         font=('Segoe UI', 8), bg=C_CARD, fg=C_MUTED).pack(side='left')

tk.Label(tab1, text="Executáveis encontrados", font=('Segoe UI', 10, 'bold'),
         bg=C_BG, fg=C_TEXTO).pack(anchor='w', padx=20, pady=(12, 4))
card_tab = tk.Frame(tab1, bg=C_CARD, highlightbackground=C_BORDA, highlightthickness=1)
card_tab.pack(fill='both', expand=True, padx=20)

lista_resultado = ttk.Treeview(card_tab, columns=('Nome', 'Caminho'),
                                show='headings', height=9, style='Prax.Treeview')
lista_resultado.heading('Nome', text='Nome do Arquivo')
lista_resultado.heading('Caminho', text='Caminho Completo')
lista_resultado.column('Nome', width=230, minwidth=130)
lista_resultado.column('Caminho', width=680, minwidth=200)
sc1 = ttk.Scrollbar(card_tab, orient='vertical', command=lista_resultado.yview)
lista_resultado.configure(yscrollcommand=sc1.set)
lista_resultado.pack(side='left', fill='both', expand=True)
sc1.pack(side='right', fill='y')

tk.Label(tab1, text="Caminhos formatados", font=('Segoe UI', 10, 'bold'),
         bg=C_BG, fg=C_TEXTO).pack(anchor='w', padx=20, pady=(10, 4))
card_paths = tk.Frame(tab1, bg=C_CARD, highlightbackground=C_BORDA, highlightthickness=1)
card_paths.pack(fill='x', padx=20, pady=(0, 10))
sc2 = tk.Scrollbar(card_paths); sc2.pack(side='right', fill='y')
caminho_texto = tk.Text(card_paths, height=4, font=('Courier New', 9),
                        bg='#0d1117', fg='#79c0ff', relief='flat', bd=0,
                        state='disabled', yscrollcommand=sc2.set, padx=10, pady=8)
caminho_texto.pack(fill='both', expand=True)
sc2.config(command=caminho_texto.yview)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Gerenciar Bloqueios
# ══════════════════════════════════════════════════════════════════════════════
tab2 = tk.Frame(notebook, bg=C_BG)
notebook.add(tab2, text="  Gerenciar Bloqueios  ")

topo2 = tk.Frame(tab2, bg=C_BG, padx=20, pady=14)
topo2.pack(fill='x')
tk.Label(topo2, text="Regras de bloqueio ativas", font=('Segoe UI', 13, 'bold'),
         bg=C_BG, fg=C_TEXTO).pack(side='left')
btn_atualizar = tk.Button(topo2, text="Atualizar Lista", command=carregar_regras,
                           font=('Segoe UI', 9), bg=C_AZUL, fg='white',
                           relief='flat', padx=14, pady=4, cursor='hand2')
btn_atualizar.pack(side='right')

aviso = tk.Frame(tab2, bg='#fff8c5', highlightbackground='#d4a72c', highlightthickness=1)
aviso.pack(fill='x', padx=20, pady=(0, 10))
tk.Label(aviso,
         text="⚠   Ao remover uma regra, o programa voltará a ter acesso à internet. "
              "Clique em 'Atualizar Lista' para carregar as regras do firewall.",
         font=('Segoe UI', 9), bg='#fff8c5', fg='#633a00',
         padx=12, pady=7, justify='left').pack(anchor='w')

card_arv = tk.Frame(tab2, bg=C_CARD, highlightbackground=C_BORDA, highlightthickness=1)
card_arv.pack(fill='both', expand=True, padx=20)

arvore_regras = ttk.Treeview(card_arv,
                              columns=('Arquivo', 'Direcao', 'Caminho'),
                              show='tree headings', height=16,
                              style='Gerenciar.Treeview', selectmode='extended')
arvore_regras.heading('#0',       text='Grupo / Pasta')
arvore_regras.heading('Arquivo',  text='Arquivo')
arvore_regras.heading('Direcao',  text='Direção')
arvore_regras.heading('Caminho',  text='Caminho Completo')
arvore_regras.column('#0',       width=200, minwidth=120)
arvore_regras.column('Arquivo',  width=190, minwidth=100)
arvore_regras.column('Direcao',  width=80,  minwidth=60)
arvore_regras.column('Caminho',  width=460, minwidth=200)
arvore_regras.tag_configure('grupo',    font=('Segoe UI', 9, 'bold'), foreground=C_AZUL)
arvore_regras.tag_configure('outbound', foreground=C_VERMELHO)
arvore_regras.tag_configure('inbound',  foreground=C_LARANJA)

sc3 = ttk.Scrollbar(card_arv, orient='vertical', command=arvore_regras.yview)
arvore_regras.configure(yscrollcommand=sc3.set)
arvore_regras.pack(side='left', fill='both', expand=True)
sc3.pack(side='right', fill='y')

bot2 = tk.Frame(tab2, bg=C_BG, padx=20, pady=8)
bot2.pack(fill='x')
tk.Label(bot2, text="Selecione uma ou mais regras (ou um grupo inteiro) para remover o bloqueio.",
         font=('Segoe UI', 9), bg=C_BG, fg=C_MUTED).pack(side='left')
tk.Button(bot2, text="  Desbloquear Selecionado  ",
          command=desbloquear_selecionado,
          font=('Segoe UI', 10, 'bold'), bg=C_LARANJA, fg='white',
          relief='flat', padx=16, pady=5, cursor='hand2').pack(side='right')

# ── Rodapé global ──────────────────────────────────────────────────────────────
rodape = tk.Frame(janela, bg=C_RODAPE, height=46)
rodape.pack(fill='x', side='bottom')
rodape.pack_propagate(False)

status_var = tk.StringVar(value="Selecione uma pasta e clique em Procurar.")
status_label = tk.Label(rodape, textvariable=status_var, font=('Segoe UI', 9),
                         bg=C_RODAPE, fg=C_MUTED, anchor='w')
status_label.pack(side='left', padx=16, pady=13)

btn_bloquear = tk.Button(rodape, text="  Bloquear Internet (Firewall)  ",
                          command=aplicar_bloqueio,
                          font=('Segoe UI', 10, 'bold'), bg=C_VERMELHO, fg='white',
                          relief='flat', padx=16, pady=4, state='disabled', cursor='hand2')
btn_bloquear.pack(side='right', padx=(0, 12), pady=8)

janela.mainloop()
