from flask import Blueprint, jsonify, request, session
from src.models.sala import Sala
from src.models.user import db

sala_bp = Blueprint('sala', __name__)

def require_auth():
    """Decorator para verificar autenticação"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    return None

@sala_bp.route('/salas', methods=['GET'])
def get_salas():
    """Obter todas as salas ativas"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        salas = Sala.query.filter_by(ativa=True).all()
        return jsonify([sala.to_dict() for sala in salas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sala_bp.route('/salas', methods=['POST'])
def create_sala():
    """Criar nova sala"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        data = request.json
        nome = data.get('nome')
        capacidade = data.get('capacidade', 10)
        
        if not nome:
            return jsonify({'error': 'Nome da sala é obrigatório'}), 400
        
        # Verificar se sala já existe
        if Sala.query.filter_by(nome=nome).first():
            return jsonify({'error': 'Sala com este nome já existe'}), 400
        
        sala = Sala(nome=nome, capacidade=capacidade)
        db.session.add(sala)
        db.session.commit()
        
        return jsonify({
            'message': 'Sala criada com sucesso',
            'sala': sala.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sala_bp.route('/salas/<int:sala_id>', methods=['GET'])
def get_sala(sala_id):
    """Obter sala específica"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        sala = Sala.query.get_or_404(sala_id)
        return jsonify(sala.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sala_bp.route('/salas/<int:sala_id>', methods=['PUT'])
def update_sala(sala_id):
    """Atualizar sala"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        sala = Sala.query.get_or_404(sala_id)
        data = request.json
        
        if 'nome' in data:
            # Verificar se novo nome já existe
            existing = Sala.query.filter_by(nome=data['nome']).first()
            if existing and existing.id != sala_id:
                return jsonify({'error': 'Sala com este nome já existe'}), 400
            sala.nome = data['nome']
        
        if 'capacidade' in data:
            sala.capacidade = data['capacidade']
        
        if 'ativa' in data:
            sala.ativa = data['ativa']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Sala atualizada com sucesso',
            'sala': sala.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sala_bp.route('/salas/<int:sala_id>', methods=['DELETE'])
def delete_sala(sala_id):
    """Desativar sala (soft delete)"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        sala = Sala.query.get_or_404(sala_id)
        sala.ativa = False
        db.session.commit()
        
        return jsonify({'message': 'Sala desativada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

