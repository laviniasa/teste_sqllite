from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Configuração do Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redireciona usuários não autenticados para a página de login

# Modelo de Usuário
# Definição dos modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Chamado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)

class Papel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    quantidade = db.Column(db.Integer, default=0)

class Toner(db.Model):
    __tablename__ = 'toners'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255))
    tipo = db.Column(db.String(100))
    quantidade = db.Column(db.Integer)
    validade = db.Column(db.Date)
    marca = db.Column(db.String(100))  # Verifique se esse campo está presente


# Criar o banco de dados (caso não exista)
with app.app_context(): 
    db.create_all()

# Inicializar usuário padrão
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if not user:
        hashed_password = generate_password_hash('123456')
        user = User(username='admin', password=hashed_password)
        db.session.add(user)
        db.session.commit()

# Carregar usuário pelo ID para sessões
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Página inicial
@app.route('/')
def index():
    toners = Toner.query.all()  # Recupera todos os toners do banco de dados
    return render_template('principal.html', toners=toners)


@app.route('/index')
@login_required
def index_page():
    try:
        toners = db.session.query(
            Toner.id,
            Toner.descricao,
            Toner.tipo,
            Toner.quantidade,
            Toner.validade
        ).order_by(Toner.descricao).all()

        papeis = Papel.query.all()
    except Exception as e:
        flash(f'Ocorreu um erro ao acessar os dados: {e}', 'danger')
        toners = []
        papeis = []

    return render_template('index.html', toners=toners, papeis=papeis)

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index_page'))  # Aqui estamos redirecionando para a nova função 'index_page'
        else:
            flash('Usuário ou senha inválidos.', 'danger')

    return render_template('login.html')

# Página protegida (somente para usuários logados)
@app.route('/dashboard')
@login_required
def dashboard():
    return f"Bem-vindo, {current_user.username}! <a href='/logout'>Logout</a>"

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

# Página principal (botão voltar redireciona aqui)
@app.route('/principal')
def principal():
    return render_template('principal.html')

# ---------------- Página de abertura de chamados --------------
@app.route('/chamado', methods=['GET', 'POST'])
def chamado():
    if request.method == 'POST':
        descricao = request.form['descricao']
        novo_chamado = Chamado(descricao=descricao)
        db.session.add(novo_chamado)
        db.session.commit()
        flash('Chamado registrado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('chamado.html')

# -----------------pagina index.html ----------------------
@app.route('/adicionar_papel', methods=['GET', 'POST'])
def adicionar_papel():
    if request.method == 'POST':
        # Lógica para adicionar papel
        papel = Papel.query.first()  # Se você tiver apenas um tipo de papel, ou pode filtrar
        if papel:
            papel.quantidade += 1  # Incrementa a quantidade de papel
        else:
            papel = Papel(descricao="Papel Padrão", quantidade=1)  # Caso não exista, cria um novo papel
            db.session.add(papel)
        
        db.session.commit()  # Salva as mudanças no banco
        flash('Papel adicionado com sucesso!', 'success')
        return redirect(url_for('index_page'))
    return render_template('adicionar_papel.html')

@app.route('/retirar_papel', methods=['POST'])
def retirar_papel():
    papel = Papel.query.first()  # Recupera o primeiro papel
    if papel and papel.quantidade > 0:
        papel.quantidade -= 1  # Decrementa a quantidade de papel
        db.session.commit()  # Salva as mudanças no banco
        flash('Papel retirado com sucesso!', 'success')
    else:
        flash('Não há papel suficiente para retirar.', 'danger')
    
    return redirect(url_for('index_page'))  # Redireciona para a página correta

@app.route('/adicionar_toner', methods=['POST'])
def adicionar_toner():
    marca = request.form['marca']  # Aqui pega a marca
    tipo = request.form['tipo']
    quantidade = int(request.form['quantidade'])  # Certifique-se de que a quantidade seja um número inteiro
    validade_str = request.form['validade']  # '2025-04-06' por exemplo
    
    # Converter a string de data para um objeto datetime.date
    validade = datetime.strptime(validade_str, '%Y-%m-%d').date()

    # Utilizar a marca como a descrição
    descricao = marca  # Agora 'descricao' é igual à marca

    # Verificar se já existe um toner com os mesmos atributos
    toner_existente = Toner.query.filter_by(
        descricao=descricao,  # Usando a marca como descrição
        tipo=tipo,
        marca=marca,
        validade=validade
    ).first()

    if toner_existente:
        # Se o toner já existir, apenas incrementar a quantidade
        toner_existente.quantidade += quantidade
        db.session.commit()
        flash(f'{quantidade} unidades do toner {toner_existente.tipo} adicionadas à quantidade existente!', 'success')
    else:
        # Caso contrário, criar um novo toner
        novo_toner = Toner(descricao=descricao, tipo=tipo, quantidade=quantidade, validade=validade, marca=marca)
        db.session.add(novo_toner)
        db.session.commit()
        flash('Toner adicionado com sucesso!', 'success')
    
    return redirect(url_for('index_page'))  # Redireciona para a página do estoque de toners

@app.route('/retirar_toner', methods=['POST'])
def retirar_toner():
    toner_id = request.form.get('toner_id')
    quantidade_retirada = int(request.form.get('quantidade', 1))

    toner = Toner.query.get(toner_id)  

    if toner:
        if toner.quantidade >= quantidade_retirada:
            toner.quantidade -= quantidade_retirada  
            db.session.commit()  
            flash(f'{quantidade_retirada} unidades do toner {toner.descricao} foram retiradas!', 'success')
        else:
            flash('Quantidade insuficiente de toner.', 'danger')
    else:
        flash('Toner não encontrado.', 'danger')

    return redirect(url_for('index_page'))  

# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)
