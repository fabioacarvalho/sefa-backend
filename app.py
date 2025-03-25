import os
import random
import string
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os



# Configurações básicas do Flask
app = Flask(__name__)
CORS(app) 
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações do Flask-Mail (ajuste conforme seu provedor de e-mail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ofabioalexcarvalho@gmail.com'
app.config['MAIL_PASSWORD'] = 'XXXXXXX'

db = SQLAlchemy(app)
mail = Mail(app)

# MODELOS DE DADOS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)

class FormSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(20), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)
    municipio = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    verification_code = db.Column(db.String(10), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# UTILITÁRIOS
def generate_verification_code(length=6):
    """Gera um código aleatório composto por dígitos."""
    return ''.join(random.choices(string.digits, k=length))

def send_verification_email(recipient, code):
    # rhrf snpr kisr ephe
    """Envia e-mail de verificação para o destinatário."""
    
    base_email = 'otestsdev@gmail.com'
    app_password = 'rhrf snpr kisr ephe'  # 🔹 Gere uma "App Password" no Google

    assunto = 'Código de Verificação'
    body = f"""
    <html>
        <body>
            <h3>Código de Verificação</h3>
            <p>Seu código de verificação é: <strong>{code}</strong></p>
        </body>
    </html>
    """

    # Configura SMTP
    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(base_email, app_password)

        # Criando mensagem formatada
        msg = MIMEMultipart()
        msg['From'] = base_email
        msg['To'] = recipient
        msg['Subject'] = assunto

        msg.attach(MIMEText(body, 'html'))

        # Enviando e-mail
        servidor.sendmail(base_email, recipient, msg.as_string())
        servidor.quit()

        print('E-mail enviado com sucesso!')
    except Exception as e:
        print(f'Erro ao enviar e-mail: {e}')



# ROTAS DA API

# 1. Cadastro de usuário
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({'error': 'Nome, email e senha são obrigatórios.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Usuário já existe.'}), 400

    hashed_password = generate_password_hash(senha)
    new_user = User(nome=nome, email=email, senha=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuário cadastrado com sucesso!'}), 201

# 1. Acesso do usuário (login)
@app.route('/sign-in', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({'error': 'Email e senha são obrigatórios.'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.senha, senha):
        return jsonify({'error': 'Credenciais inválidas.'}), 401

    # Aqui você pode gerar um token JWT para autenticação futura
    return jsonify({'user': { 'id': user.id, 'nome': user.nome, 'email': user.email }, 'message': 'Login realizado com sucesso!'}), 200

# 2. Obter lista de municípios (autofill)
@app.route('/municipios', methods=['GET'])
def get_municipios():
    try:
        # Lê o arquivo Excel
        df = pd.read_excel('municipios.xlsx')
        
        # Remove espaços extras nos nomes das colunas (caso existam)
        df.columns = df.columns.str.strip()

        # Verifica se a coluna correta existe
        if 'Nome_Municipio' not in df.columns:
            return jsonify({'error': f'Coluna não encontrada. Colunas disponíveis: {df.columns.tolist()}'}), 500

        # Retorna a lista de municípios
        municipios = df['Nome_Municipio'].dropna().tolist()
        return jsonify({'municipios': municipios}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao ler a planilha: {str(e)}'}), 500

# 3. Cadastro do formulário com pré-save e envio de código de verificação
@app.route('/form', methods=['POST'])
def create_form():
    data = request.get_json()
    nome = data.get('nome')
    cpf = data.get('cpf')
    cargo = data.get('cargo')
    municipio = data.get('municipio')
    email = data.get('email')

    # Valida os campos obrigatórios
    if not all([nome, cpf, cargo, municipio, email]):
        return jsonify({'error': 'Todos os campos do formulário são obrigatórios.'}), 400

    # Gera um código de verificação
    code = generate_verification_code()

    # Cria o registro com is_verified False
    form_submission = FormSubmission(
        nome=nome,
        cpf=cpf,
        cargo=cargo,
        municipio=municipio,
        email=email,
        verification_code=code,
        is_verified=False
    )
    db.session.add(form_submission)
    db.session.commit()

    # try:
    #     # Envia o código de verificação para o e-mail informado
    #     send_verification_email(email, code)
    # except Exception as e:
    #     return jsonify({'error': f'Falha ao enviar e-mail: {str(e)}'}), 500

    return jsonify({
        'message': 'Código de verificação enviado. Por favor, confirme para concluir o cadastro do formulário.',
        'form_id': form_submission.id,
        'verification_code': code
    }), 201

# 3. Verificação do código e finalização do cadastro do formulário
@app.route('/verify', methods=['POST'])
def verify_form():
    data = request.get_json()
    form_id = data.get('form_id')
    code = data.get('code')

    if not form_id or not code:
        return jsonify({'error': 'ID do formulário e código são obrigatórios.'}), 400

    form_submission = FormSubmission.query.get(form_id)
    if not form_submission:
        return jsonify({'error': 'Formulário não encontrado.'}), 404

    if form_submission.verification_code != code:
        return jsonify({'error': 'Código de verificação inválido.'}), 400

    # Atualiza o status para verificado
    form_submission.is_verified = True
    db.session.commit()

    return jsonify({'message': 'Formulário verificado e salvo com sucesso!'}), 200

@app.route('/forms', methods=['GET'])
def get_form():
    form_submissions = FormSubmission.query.all()
    infos = [{
        'id': form.id,
        'nome': form.nome,
        'cpf': form.cpf,
        'cargo': form.cargo,
        'municipio': form.municipio,
        'email': form.email,
        'is_verified': form.is_verified,
        'created_at': form.created_at
    } for form in form_submissions if form.is_verified == True]

    return jsonify({'forms': infos}), 200


# Inicializa o banco de dados (criar as tabelas)
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    app.run()
    # app.run(host="0.0.0.0", port=8000, debug=True)  # For Docker
