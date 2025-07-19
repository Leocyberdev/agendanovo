from flask import Blueprint, jsonify, request, session
from datetime import datetime
from src.models.user import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Rota para fazer login"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username e password são obrigatórios'}), 400
        
        # Buscar usuário
        user = User.query.filter_by(username=username, ativo=True).first()
        
        if user and user.check_password(password):
            # Login bem-sucedido
            session['user_id'] = user.id
            session['username'] = user.username
            
            # Atualizar último login
            user.ultimo_login = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Login realizado com sucesso',
                'user': user.to_dict_safe()
            }), 200
        else:
            return jsonify({'error': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Rota para fazer logout"""
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Rota para registrar novo usuário"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'error': 'Username, email e password são obrigatórios'}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username já existe'}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email já está em uso'}), 400
        
        # Criar novo usuário
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': user.to_dict_safe()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Rota para obter informações do usuário logado"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    user = User.query.get(session['user_id'])
    if not user or not user.ativo:
        session.clear()
        return jsonify({'error': 'Usuário não encontrado'}), 401
    
    return jsonify({'user': user.to_dict_safe()}), 200

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Verifica se o usuário está autenticado"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.ativo:
            return jsonify({'authenticated': True, 'user': user.to_dict_safe()}), 200
    
    return jsonify({'authenticated': False}), 200

