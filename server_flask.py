from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import time
import json
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'chave_secreta_escolar'

# Variável global para controle de versão dos dados
ultima_atualizacao = 0

# Arquivo para armazenar as mensagens do chat
CHAT_FILE = "chat_messages.json"

# Inicializar arquivo de chat se não existir
def init_chat_file():
    if not os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

# Carregar mensagens do chat
def carregar_mensagens():
    init_chat_file()
    try:
        with open(CHAT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# Salvar nova mensagem
def salvar_mensagem(usuario, mensagem):
    mensagens = carregar_mensagens()
    nova_mensagem = {
        'usuario': usuario,
        'mensagem': mensagem,
        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'perfil': session.get('perfil', 'usuario')
    }
    mensagens.append(nova_mensagem)
    
    # Manter apenas as últimas 100 mensagens
    if len(mensagens) > 100:
        mensagens = mensagens[-100:]
    
    with open(CHAT_FILE, 'w', encoding='utf-8') as f:
        json.dump(mensagens, f, ensure_ascii=False, indent=2)

def caminhos():
    pasta = os.path.dirname(os.path.abspath(__file__))
    caminho_turmas = os.path.join(pasta, "output", "output", "turmas.txt")
    caminho_alunos = os.path.join(pasta, "output", "output", "alunos.txt")
    return caminho_turmas, caminho_alunos

def get_timestamp_arquivos():
    """Retorna o timestamp da última modificação dos arquivos"""
    caminho_turmas, caminho_alunos = caminhos()
    timestamps = []
    
    for arquivo in [caminho_turmas, caminho_alunos]:
        if os.path.exists(arquivo):
            timestamps.append(os.path.getmtime(arquivo))
    
    return max(timestamps) if timestamps else 0

def carregar_dados():
    global ultima_atualizacao
    
    caminho_turmas, caminho_alunos = caminhos()
    
    dados = {
        'alunos': [],
        'turmas': {},
        'erro': None,
        'timestamp': get_timestamp_arquivos()
    }
    
    if not os.path.exists(caminho_turmas) or not os.path.exists(caminho_alunos):
        dados['erro'] = "Arquivos não encontrados. Execute os programas C primeiro."
        return dados
    
    # Carregar turmas - ACEITA TEXTO E NÚMEROS
    try:
        with open(caminho_turmas, "r", encoding="utf-8") as t:
            for linha in t.readlines():
                partes = linha.strip().split(",")
                if len(partes) == 2:
                    codigo = partes[0].strip()  # Mantém como string
                    nome_turma = partes[1].strip()
                    dados['turmas'][codigo] = nome_turma
    except Exception as e:
        dados['erro'] = f"Erro ao carregar turmas: {str(e)}"
        return dados
    
    # Carregar alunos - ACEITA TEXTO E NÚMEROS
    try:
        with open(caminho_alunos, "r", encoding="utf-8") as a:
            for linha in a:
                dados_aluno = linha.strip().split(",")
                if len(dados_aluno) == 7:
                    cod_turma, matricula, nome, np1, np2, pim, media = dados_aluno
                    
                    # Converte notas para float com tratamento de erro
                    try:
                        np1_float = float(np1)
                        np2_float = float(np2)
                        pim_float = float(pim)
                        media_float = float(media)
                    except ValueError:
                        # Se não conseguir converter, usa zeros
                        np1_float = 0.0
                        np2_float = 0.0
                        pim_float = 0.0
                        media_float = 0.0
                    
                    situacao = "APROVADO" if media_float >= 7 else "REPROVADO"
                    
                    # Busca o nome da turma (aceita texto)
                    turma_nome = dados['turmas'].get(cod_turma, "Não encontrada")
                    
                    dados['alunos'].append({
                        'cod_turma': cod_turma,
                        'turma_nome': turma_nome,
                        'matricula': matricula,
                        'nome': nome,
                        'np1': f"{np1_float:.1f}",
                        'np2': f"{np2_float:.1f}",
                        'pim': f"{pim_float:.1f}",
                        'media': f"{media_float:.2f}",
                        'situacao': situacao,
                        'cor': 'table-success' if media_float >= 7 else 'table-danger'
                    })
    except Exception as e:
        dados['erro'] = f"Erro ao carregar alunos: {str(e)}"
    
    ultima_atualizacao = dados['timestamp']
    return dados

def salvar_aluno(cod_turma, matricula, nome, np1, np2, pim):
    """Salva um novo aluno no arquivo"""
    try:
        np1_float = float(np1)
        np2_float = float(np2)
        pim_float = float(pim)
        media = np1_float * 0.4 + np2_float * 0.4 + pim_float * 0.2
    except ValueError:
        media = 0.0
    
    nova_linha = f"{cod_turma},{matricula},{nome},{np1},{np2},{pim},{media:.2f}\n"
    
    caminho_turmas, caminho_alunos = caminhos()
    
    with open(caminho_alunos, 'a', encoding='utf-8') as f:
        f.write(nova_linha)

def atualizar_aluno(nome_antigo, novo_cod_turma, nova_matricula, novo_nome, np1, np2, pim):
    """Atualiza um aluno existente"""
    try:
        np1_float = float(np1)
        np2_float = float(np2)
        pim_float = float(pim)
        media = np1_float * 0.4 + np2_float * 0.4 + pim_float * 0.2
    except ValueError:
        media = 0.0
    
    caminho_turmas, caminho_alunos = caminhos()
    
    with open(caminho_alunos, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    for i, linha in enumerate(linhas):
        dados = linha.strip().split(',')
        if len(dados) >= 3 and dados[2] == nome_antigo:
            linhas[i] = f"{novo_cod_turma},{nova_matricula},{novo_nome},{np1},{np2},{pim},{media:.2f}\n"
            break
    
    with open(caminho_alunos, 'w', encoding='utf-8') as f:
        f.writelines(linhas)

def remover_aluno(nome):
    """Remove um aluno do arquivo"""
    caminho_turmas, caminho_alunos = caminhos()
    
    with open(caminho_alunos, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    novas_linhas = []
    for linha in linhas:
        dados = linha.strip().split(',')
        if len(dados) >= 3 and dados[2] != nome:
            novas_linhas.append(linha)
    
    with open(caminho_alunos, 'w', encoding='utf-8') as f:
        f.writelines(novas_linhas)

def salvar_turma(codigo, nome):
    """Salva uma nova turma no arquivo"""
    nova_linha = f"{codigo},{nome}\n"
    
    caminho_turmas, caminho_alunos = caminhos()
    
    with open(caminho_turmas, 'a', encoding='utf-8') as f:
        f.write(nova_linha)

def remover_turma(codigo):
    """Remove uma turma do arquivo"""
    caminho_turmas, caminho_alunos = caminhos()
    
    with open(caminho_turmas, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    novas_linhas = []
    for linha in linhas:
        dados = linha.strip().split(',')
        if len(dados) == 2 and dados[0] != codigo:
            novas_linhas.append(linha)
    
    with open(caminho_turmas, 'w', encoding='utf-8') as f:
        f.writelines(novas_linhas)

# ---------------- FUNÇÕES DE RELATÓRIOS ---------------- 
def gerar_relatorio_estatisticas(dados):
    total_alunos = len(dados['alunos'])
    aprovados = len([a for a in dados['alunos'] if a['situacao'] == 'APROVADO'])
    reprovados = total_alunos - aprovados
    taxa_aprovacao = (aprovados / total_alunos * 100) if total_alunos > 0 else 0
    
    # Médias gerais
    medias = [float(aluno['media']) for aluno in dados['alunos']]
    media_geral = sum(medias) / len(medias) if medias else 0
    
    # Estatísticas por turma
    stats_turmas = {}
    for cod_turma, nome_turma in dados['turmas'].items():
        alunos_turma = [a for a in dados['alunos'] if a['cod_turma'] == cod_turma]
        if alunos_turma:
            aprovados_turma = len([a for a in alunos_turma if a['situacao'] == 'APROVADO'])
            stats_turmas[cod_turma] = {
                'nome': nome_turma,
                'total': len(alunos_turma),
                'aprovados': aprovados_turma,
                'taxa': round((aprovados_turma / len(alunos_turma) * 100), 2)
            }
    
    return {
        'total_alunos': total_alunos,
        'aprovados': aprovados,
        'reprovados': reprovados,
        'taxa_aprovacao': round(taxa_aprovacao, 2),
        'media_geral': round(media_geral, 2),
        'total_turmas': len(dados['turmas']),
        'turmas': stats_turmas
    }

def gerar_relatorio_aprovacao(dados):
    relatorio = {}
    for cod_turma, nome_turma in dados['turmas'].items():
        alunos_turma = [a for a in dados['alunos'] if a['cod_turma'] == cod_turma]
        aprovados = len([a for a in alunos_turma if a['situacao'] == 'APROVADO'])
        total = len(alunos_turma)
        
        relatorio[cod_turma] = {
            'nome_turma': nome_turma,
            'total_alunos': total,
            'aprovados': aprovados,
            'reprovados': total - aprovados,
            'taxa_aprovacao': round((aprovados / total * 100), 2) if total > 0 else 0
        }
    
    return relatorio

def gerar_relatorio_turmas(dados):
    relatorio = {}
    for cod_turma, nome_turma in dados['turmas'].items():
        alunos_turma = [a for a in dados['alunos'] if a['cod_turma'] == cod_turma]
        
        if alunos_turma:
            medias = [float(a['media']) for a in alunos_turma]
            media_turma = sum(medias) / len(medias)
            melhor_aluno = max(alunos_turma, key=lambda x: float(x['media']))
            pior_aluno = min(alunos_turma, key=lambda x: float(x['media']))
        else:
            media_turma = 0
            melhor_aluno = None
            pior_aluno = None
        
        relatorio[cod_turma] = {
            'nome_turma': nome_turma,
            'total_alunos': len(alunos_turma),
            'media_turma': round(media_turma, 2),
            'melhor_aluno': melhor_aluno,
            'pior_aluno': pior_aluno
        }
    
    return relatorio

def exportar_csv(dados):
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # Cabeçalho
    writer.writerow(['Turma', 'Código Turma', 'Matrícula', 'Aluno', 'NP1', 'NP2', 'PIM', 'Média', 'Situação'])
    
    # Dados
    for aluno in dados['alunos']:
        writer.writerow([
            aluno['turma_nome'],
            aluno['cod_turma'],
            aluno['matricula'],
            aluno['nome'],
            aluno['np1'],
            aluno['np2'],
            aluno['pim'],
            aluno['media'],
            aluno['situacao']
        ])
    
    from flask import Response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=relatorio_alunos.csv"}
    )

# Arquivo para armazenar as faltas
FALTAS_FILE = "faltas.json"

def init_faltas_file():
    if not os.path.exists(FALTAS_FILE):
        with open(FALTAS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)

def carregar_faltas():
    init_faltas_file()
    try:
        with open(FALTAS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def salvar_faltas(faltas):
    with open(FALTAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(faltas, f, ensure_ascii=False, indent=2)

def registrar_falta(aluno_matricula, data, turma_codigo):
    faltas = carregar_faltas()
    
    if turma_codigo not in faltas:
        faltas[turma_codigo] = {}
    
    if aluno_matricula not in faltas[turma_codigo]:
        faltas[turma_codigo][aluno_matricula] = []
    
    # Verifica se já não existe falta nesta data
    if data not in faltas[turma_codigo][aluno_matricula]:
        faltas[turma_codigo][aluno_matricula].append(data)
    
    salvar_faltas(faltas)
    return True

def remover_falta(aluno_matricula, data, turma_codigo):
    faltas = carregar_faltas()
    
    if (turma_codigo in faltas and 
        aluno_matricula in faltas[turma_codigo] and 
        data in faltas[turma_codigo][aluno_matricula]):
        
        faltas[turma_codigo][aluno_matricula].remove(data)
        salvar_faltas(faltas)
        return True
    
    return False

def get_faltas_aluno(aluno_matricula, turma_codigo):
    faltas = carregar_faltas()
    if turma_codigo in faltas and aluno_matricula in faltas[turma_codigo]:
        return faltas[turma_codigo][aluno_matricula]
    return []

def get_total_faltas_aluno(aluno_matricula, turma_codigo):
    return len(get_faltas_aluno(aluno_matricula, turma_codigo))

# Arquivo simples para armazenar faltas
FALTAS_FILE = "faltas.txt"

def carregar_faltas():
    try:
        with open(FALTAS_FILE, 'r', encoding='utf-8') as f:
            faltas = {}
            for linha in f:
                dados = linha.strip().split(',')
                if len(dados) == 3:
                    matricula, data, turma = dados
                    if matricula not in faltas:
                        faltas[matricula] = []
                    faltas[matricula].append({'data': data, 'turma': turma})
            return faltas
    except:
        return {}

def salvar_falta(matricula, data, turma):
    try:
        with open(FALTAS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{matricula},{data},{turma}\n")
        return True
    except:
        return False

# ---------------- ROTA DE CHAT COM IA ---------------- 
@app.route('/chat_ia', methods=['POST'])
def chat_ia():
    if 'perfil' not in session:
        return jsonify({'erro': 'Não autenticado'}), 401
    
    mensagem = request.form.get('mensagem', '').strip()
    if not mensagem:
        return jsonify({'erro': 'Mensagem vazia'}), 400
    
    try:
        # Gera resposta da IA simulada
        resposta_simulada = gerar_resposta_ia(mensagem)
        
        return jsonify({
            'status': 'sucesso',
            'resposta': resposta_simulada,
            'timestamp': datetime.now().strftime('%H:%M')
        })
    except Exception as e:
        return jsonify({'erro': f'Erro na IA: {str(e)}'}), 500

def gerar_resposta_ia(mensagem):
    """Gera uma resposta simulada da IA baseada na mensagem do usuário"""
    mensagem_lower = mensagem.lower()
    
    # Respostas pré-definidas baseadas em palavras-chave
    respostas_notas = [
        "Suas notas são calculadas da seguinte forma: NP1 (40%) + NP2 (40%) + PIM (20%). Para ser aprovado, você precisa de média igual ou superior a 7.0.",
        "O cálculo da média é: (NP1 × 0.4) + (NP2 × 0.4) + (PIM × 0.2). A aprovação requer média ≥ 7.0. Se estiver com dificuldades, recomendo conversar com seu professor.",
        "As notas NP1 e NP2 valem 40% cada, e o PIM vale 20%. Sua média final precisa ser 7.0 ou mais para aprovação."
    ]
    
    respostas_estudo = [
        "Para melhorar seu aprendizado, sugiro: revisar as aulas regularmente, fazer exercícios práticos e não acumular dúvidas.",
        "Métodos eficazes de estudo incluem: fazer resumos, praticar com exercícios, estudar em grupo e revisar o conteúdo antes das provas.",
        "Organize seu tempo de estudo: dedique pelo menos 1-2 horas por dia, faça pausas regulares e priorize as matérias com mais dificuldade."
    ]
    
    respostas_pim = [
        "O PIM (Projeto Integrado Multidisciplinar) vale 20% da sua média final. É importante começar cedo e seguir as orientações do professor.",
        "Para o PIM: escolha um tema relevante, faça um planejamento detalhado, pesquise em fontes confiáveis e revise o trabalho antes de entregar.",
        "O PIM é uma oportunidade para aplicar o conhecimento prático. Divida o projeto em etapas e busque ajuda do professor se tiver dúvidas."
    ]
    
    respostas_faltas = [
        "As faltas podem impactar seu aprendizado. Mantenha uma boa frequência para não perder conteúdo importante das aulas.",
        "Cada turma tem regras específicas sobre frequência. Consulte a secretaria ou seu coordenador para saber os detalhes.",
        "A frequência é importante para acompanhar o ritmo da turma. Evite faltas desnecessárias e comunique-se com os professores quando necessário."
    ]
    
    respostas_gerais = [
        "Entendi sua pergunta! Posso ajudar com dúvidas sobre: notas, métodos de estudo, PIM, frequência e organização do tempo.",
        "Como assistente educacional, posso esclarecer dúvidas sobre seu desempenho acadêmico e métodos de estudo. Pode me contar mais?",
        "Compreendo sua questão! Posso orientar sobre notas, estudos, projetos e frequência. Há algo específico que gostaria de saber?"
    ]
    
    # Verifica palavras-chave e seleciona resposta apropriada
    if any(palavra in mensagem_lower for palavra in ['nota', 'prova', 'avaliação', 'np1', 'np2', 'pim', 'média', 'calcular']):
        return random.choice(respostas_notas)
    
    elif any(palavra in mensagem_lower for palavra in ['estudar', 'estudo', 'aprender', 'material', 'como estudar', 'dica']):
        return random.choice(respostas_estudo)
    
    elif any(palavra in mensagem_lower for palavra in ['pim', 'projeto', 'trabalho', 'entregar']):
        return random.choice(respostas_pim)
    
    elif any(palavra in mensagem_lower for palavra in ['falta', 'presença', 'aula', 'frequência']):
        return random.choice(respostas_faltas)
    
    elif any(palavra in mensagem_lower for palavra in ['olá', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'hello']):
        return "Olá! Sou seu assistente de estudos. Como posso ajudá-lo hoje? Posso esclarecer dúvidas sobre notas, matérias, métodos de estudo e muito mais!"
    
    elif any(palavra in mensagem_lower for palavra in ['obrigado', 'obrigada', 'valeu', 'agradeço', 'thanks']):
        return random.choice([
            "De nada! Fico feliz em ajudar. Se tiver mais alguma dúvida, estou aqui! 😊",
            "Por nada! Estou à disposição para ajudar no que precisar.",
            "Imagina! Fico contente em poder ajudar. Volte sempre que tiver dúvidas!"
        ])
    
    else:
        return random.choice(respostas_gerais)

# ---------------- ROTAS ---------------- 
@app.route('/')
def index():
    # SEMPRE vai para o login primeiro
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Se já estiver logado, vai direto para o dashboard
    if 'perfil' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip().lower()
        senha = request.form.get('senha', '').strip().lower()
        
        perfis_validos = {
            'aluno': 'aluno',
            'professor': 'professor', 
            'diretor': 'diretor'
        }
        
        if usuario in perfis_validos and senha == perfis_validos[usuario]:
            session['perfil'] = usuario
            session['nome_perfil'] = usuario.capitalize()
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', erro="Usuário ou senha incorretos")
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'perfil' not in session:
        return redirect(url_for('login'))
    
    dados = carregar_dados()
    perfil = session['perfil']
    
    # Templates específicos para cada perfil
    if perfil == 'diretor':
        return render_template('dashboard_diretor.html', 
                             dados=dados, 
                             perfil=perfil,
                             nome_perfil=session['nome_perfil'])
    elif perfil == 'professor':
        return render_template('dashboard_professor.html', 
                             dados=dados, 
                             perfil=perfil,
                             nome_perfil=session['nome_perfil'])
    else:
        # Para aluno, usa o dashboard original
        return render_template('dashboard.html', 
                             dados=dados, 
                             perfil=perfil,
                             nome_perfil=session['nome_perfil'])

@app.route('/api/dados')
def api_dados():
    if 'perfil' not in session:
        return jsonify({'erro': 'Não autenticado'}), 401
    
    dados = carregar_dados()
    return jsonify(dados)

@app.route('/api/check_updates')
def check_updates():
    """API para verificar se há atualizações"""
    current_timestamp = get_timestamp_arquivos()
    return jsonify({
        'updated': current_timestamp > ultima_atualizacao,
        'timestamp': current_timestamp
    })

@app.route('/editar_aluno', methods=['POST'])
def editar_aluno():
    if 'perfil' not in session:
        return redirect(url_for('login'))
    
    if session['perfil'] == 'aluno':
        return "Aluno não pode editar notas", 403
    
    nome_antigo = request.form.get('nome_antigo')
    cod_turma = request.form.get('cod_turma')
    matricula = request.form.get('matricula')
    nome = request.form.get('nome')
    np1 = request.form.get('np1')
    np2 = request.form.get('np2')
    pim = request.form.get('pim')
    
    try:
        atualizar_aluno(nome_antigo, cod_turma, matricula, nome, np1, np2, pim)
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Erro: {str(e)}", 500

@app.route('/adicionar_aluno', methods=['POST'])
def adicionar_aluno():
    if 'perfil' not in session:
        return redirect(url_for('login'))
    
    if session['perfil'] != 'diretor':
        return "Apenas diretor pode adicionar alunos", 403
    
    cod_turma = request.form.get('cod_turma')
    matricula = request.form.get('matricula')
    nome = request.form.get('nome')
    
    try:
        salvar_aluno(cod_turma, matricula, nome, 0, 0, 0)
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Erro: {str(e)}", 500

@app.route('/remover_aluno', methods=['POST'])
def remover_aluno_route():
    if 'perfil' not in session:
        return redirect(url_for('login'))
    
    if session['perfil'] != 'diretor':
        return "Apenas diretor pode remover alunos", 403
    
    nome = request.form.get('nome')
    
    try:
        remover_aluno(nome)
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Erro: {str(e)}", 500

@app.route('/adicionar_turma', methods=['POST'])
def adicionar_turma():
    if 'perfil' not in session:
        return redirect(url_for('login'))
    
    if session['perfil'] != 'diretor':
        return "Apenas diretor pode adicionar turmas", 403
    
    codigo = request.form.get('codigo')
    nome = request.form.get('nome')
    
    try:
        salvar_turma(codigo, nome)
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Erro: {str(e)}", 500

@app.route('/remover_turma', methods=['POST'])
def remover_turma_route():
    if 'perfil' not in session:
        return redirect(url_for('login'))
    
    if session['perfil'] != 'diretor':
        return "Apenas diretor pode remover turmas", 403
    
    codigo = request.form.get('codigo')
    
    try:
        remover_turma(codigo)
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Erro: {str(e)}", 500

@app.route('/chat_mensagens')
def chat_mensagens():
    if 'perfil' not in session:
        return jsonify({'erro': 'Não autenticado'}), 401
    return jsonify(carregar_mensagens())

@app.route('/enviar_mensagem', methods=['POST'])
def enviar_mensagem():
    if 'perfil' not in session:
        return jsonify({'erro': 'Não autenticado'}), 401
    
    mensagem = request.form.get('mensagem', '').strip()
    if mensagem:
        salvar_mensagem(session['nome_perfil'], mensagem)
        return jsonify({'status': 'sucesso'})
    
    return jsonify({'erro': 'Mensagem vazia'}), 400

# ---------------- NOVAS ROTAS PARA RELATÓRIOS ---------------- 

@app.route('/relatorios')
def relatorios():
    if 'perfil' not in session or session['perfil'] != 'diretor':
        return "Acesso negado", 403
    
    dados = carregar_dados()
    return render_template('relatorios.html', 
                         dados=dados,
                         perfil=session['perfil'],
                         nome_perfil=session['nome_perfil'])

@app.route('/api/relatorio/<tipo>')
def api_relatorio(tipo):
    if 'perfil' not in session or session['perfil'] != 'diretor':
        return jsonify({'erro': 'Acesso negado'}), 403
    
    dados = carregar_dados()
    
    if tipo == 'estatisticas':
        return jsonify(gerar_relatorio_estatisticas(dados))
    elif tipo == 'aprovacao':
        return jsonify(gerar_relatorio_aprovacao(dados))
    elif tipo == 'turmas':
        return jsonify(gerar_relatorio_turmas(dados))
    else:
        return jsonify({'erro': 'Tipo de relatório inválido'}), 400

@app.route('/exportar/<tipo>')
def exportar_relatorio(tipo):
    if 'perfil' not in session or session['perfil'] != 'diretor':
        return "Acesso negado", 403
    
    dados = carregar_dados()
    
    if tipo == 'csv':
        return exportar_csv(dados)
    elif tipo == 'pdf':
        # Placeholder para PDF - você pode implementar depois
        return "PDF em desenvolvimento - use CSV por enquanto", 400
    else:
        return "Formato inválido", 400

# ---------------- ROTAS DE FALTAS ---------------- 
@app.route('/faltas')
def gerenciar_faltas():
    if 'perfil' not in session or session['perfil'] not in ['professor', 'diretor']:
        return "Acesso negado", 403
    
    dados = carregar_dados()
    faltas = carregar_faltas()
    
    return render_template('faltas.html', 
                         dados=dados,
                         faltas=faltas,
                         perfil=session['perfil'],
                         nome_perfil=session['nome_perfil'])

@app.route('/registrar_falta', methods=['POST'])
def registrar_falta_route():
    if 'perfil' not in session or session['perfil'] not in ['professor', 'diretor']:
        return jsonify({'erro': 'Acesso negado'}), 403
    
    aluno_matricula = request.form.get('matricula')
    data = request.form.get('data')
    turma_codigo = request.form.get('turma_codigo')
    
    if registrar_falta(aluno_matricula, data, turma_codigo):
        return jsonify({'status': 'sucesso'})
    else:
        return jsonify({'erro': 'Erro ao registrar falta'}), 400

@app.route('/remover_falta', methods=['POST'])
def remover_falta_route():
    if 'perfil' not in session or session['perfil'] not in ['professor', 'diretor']:
        return jsonify({'erro': 'Acesso negado'}), 403
    
    aluno_matricula = request.form.get('matricula')
    data = request.form.get('data')
    turma_codigo = request.form.get('turma_codigo')
    
    if remover_falta(aluno_matricula, data, turma_codigo):
        return jsonify({'status': 'sucesso'})
    else:
        return jsonify({'erro': 'Erro ao remover falta'}), 400

@app.route('/api/faltas/<turma_codigo>')
def api_faltas_turma(turma_codigo):
    if 'perfil' not in session or session['perfil'] not in ['professor', 'diretor']:
        return jsonify({'erro': 'Acesso negado'}), 403
    
    faltas = carregar_faltas()
    return jsonify(faltas.get(turma_codigo, {}))

@app.route('/minhas_turmas')
def minhas_turmas():
    if 'perfil' not in session or session['perfil'] not in ['professor', 'diretor']:
        return "Acesso negado", 403
    
    try:
        dados = carregar_dados()
        print(f"✅ Carregando minhas_turmas - {len(dados['turmas'])} turmas, {len(dados['alunos'])} alunos")
        
        return render_template('minhas_turmas.html', 
                             dados=dados,
                             perfil=session['perfil'],
                             nome_perfil=session['nome_perfil'])
    except Exception as e:
        print(f"❌ Erro em minhas_turmas: {e}")
        return f"Erro: {e}", 500

@app.route('/registrar_falta_simples', methods=['POST'])
def registrar_falta_simples():
    if 'perfil' not in session or session['perfil'] not in ['professor', 'diretor']:
        return jsonify({'erro': 'Acesso negado'}), 403
    
    matricula = request.form.get('matricula')
    data = request.form.get('data')
    turma = request.form.get('turma')
    
    if salvar_falta(matricula, data, turma):
        return jsonify({'status': 'sucesso', 'mensagem': 'Falta registrada!'})
    else:
        return jsonify({'erro': 'Erro ao registrar falta'}), 500

@app.route('/api/faltas_aluno/<matricula>')
def api_faltas_aluno(matricula):
    if 'perfil' not in session:
        return jsonify({'erro': 'Acesso negado'}), 403
    
    faltas = carregar_faltas()
    return jsonify(faltas.get(matricula, []))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print("🌐 Servidor rodando em: http://192.168.0.2:5000")
    print("📱 Acesse de outros dispositivos na rede usando seu IP")
    app.run(host='0.0.0.0', port=5000, debug=True)
    