from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
from src.models.reuniao import Reuniao
from src.models.sala import Sala
from src.models.user import User, db
from src.utils.email_service import enviar_notificacao_agendamento, enviar_notificacao_cancelamento
import logging

reuniao_bp = Blueprint('reuniao', __name__)

def require_auth():
    """Decorator para verificar autenticação"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    return None

@reuniao_bp.route('/reunioes', methods=['GET'])
def get_reunioes():
    """Obter todas as reuniões ativas"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        # Parâmetros opcionais para filtrar
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        sala_id = request.args.get('sala_id')
        
        query = Reuniao.query.filter_by(ativa=True)
        
        if data_inicio:
            data_inicio_dt = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
            query = query.filter(Reuniao.data_fim >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
            query = query.filter(Reuniao.data_inicio <= data_fim_dt)
        
        if sala_id:
            query = query.filter_by(sala_id=sala_id)
        
        reunioes = query.order_by(Reuniao.data_inicio).all()
        return jsonify([reuniao.to_dict() for reuniao in reunioes]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reuniao_bp.route('/reunioes', methods=['POST'])
def create_reuniao():
    """Criar nova reunião"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        data = request.json
        titulo = data.get('titulo')
        descricao = data.get('descricao', '')
        data_inicio_str = data.get('data_inicio')
        data_fim_str = data.get('data_fim')
        sala_id = data.get('sala_id')
        participantes_ids = data.get('participantes', [])
        
        # Validações básicas
        if not titulo or not data_inicio_str or not data_fim_str or not sala_id:
            return jsonify({'error': 'Título, data de início, data de fim e sala são obrigatórios'}), 400
        
        # Converter strings para datetime
        try:
            data_inicio = datetime.fromisoformat(data_inicio_str.replace('Z', '+00:00'))
            data_fim = datetime.fromisoformat(data_fim_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Formato de data inválido. Use ISO format'}), 400
        
        # Validar se data de fim é posterior à data de início
        if data_fim <= data_inicio:
            return jsonify({'error': 'Data de fim deve ser posterior à data de início'}), 400
        
        # Verificar se a sala existe
        sala = Sala.query.get(sala_id)
        if not sala or not sala.ativa:
            return jsonify({'error': 'Sala não encontrada ou inativa'}), 400
        
        # Verificar conflitos de horário na sala
        conflitos_sala = Reuniao.verificar_conflito_horario(sala_id, data_inicio, data_fim)
        if conflitos_sala:
            conflito_info = []
            for conflito in conflitos_sala:
                conflito_info.append({
                    'titulo': conflito.titulo,
                    'data_inicio': conflito.data_inicio.isoformat(),
                    'data_fim': conflito.data_fim.isoformat()
                })
            return jsonify({
                'error': 'Conflito de horário na sala (considerando buffer de 10 minutos)',
                'conflitos': conflito_info
            }), 409
        
        # Verificar disponibilidade dos participantes
        participantes_indisponiveis = []
        participantes_validos = []
        
        for participante_id in participantes_ids:
            user = User.query.get(participante_id)
            if not user or not user.ativo:
                return jsonify({'error': f'Participante com ID {participante_id} não encontrado'}), 400
            
            if not Reuniao.verificar_disponibilidade_participante(participante_id, data_inicio, data_fim):
                participantes_indisponiveis.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                })
            else:
                participantes_validos.append(user)
        
        if participantes_indisponiveis:
            return jsonify({
                'error': 'Alguns participantes não estão disponíveis no horário solicitado',
                'participantes_indisponiveis': participantes_indisponiveis
            }), 409
        
        # Criar a reunião
        reuniao = Reuniao(
            titulo=titulo,
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim=data_fim,
            sala_id=sala_id,
            criador_id=session['user_id']
        )
        
        # Adicionar participantes
        reuniao.participantes = participantes_validos
        
        db.session.add(reuniao)
        db.session.commit()
        
        # Enviar notificações por email
        try:
            if participantes_validos:
                emails_enviados = enviar_notificacao_agendamento(reuniao, participantes_validos)
                logging.info(f"Emails de agendamento enviados: {emails_enviados}/{len(participantes_validos)}")
        except Exception as e:
            logging.error(f"Erro ao enviar emails de agendamento: {str(e)}")
            # Não falhar a criação da reunião por causa do email
        
        return jsonify({
            'message': 'Reunião criada com sucesso',
            'reuniao': reuniao.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reuniao_bp.route('/reunioes/<int:reuniao_id>', methods=['GET'])
def get_reuniao(reuniao_id):
    """Obter reunião específica"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        reuniao = Reuniao.query.get_or_404(reuniao_id)
        return jsonify(reuniao.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reuniao_bp.route('/reunioes/<int:reuniao_id>', methods=['PUT'])
def update_reuniao(reuniao_id):
    """Atualizar reunião"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        reuniao = Reuniao.query.get_or_404(reuniao_id)
        data = request.json
        
        # Verificar se o usuário pode editar (criador da reunião)
        if reuniao.criador_id != session['user_id']:
            return jsonify({'error': 'Apenas o criador da reunião pode editá-la'}), 403
        
        # Atualizar campos básicos
        if 'titulo' in data:
            reuniao.titulo = data['titulo']
        
        if 'descricao' in data:
            reuniao.descricao = data['descricao']
        
        # Atualizar datas se fornecidas
        data_inicio_alterada = False
        data_fim_alterada = False
        
        if 'data_inicio' in data:
            try:
                nova_data_inicio = datetime.fromisoformat(data['data_inicio'].replace('Z', '+00:00'))
                if nova_data_inicio != reuniao.data_inicio:
                    reuniao.data_inicio = nova_data_inicio
                    data_inicio_alterada = True
            except ValueError:
                return jsonify({'error': 'Formato de data de início inválido'}), 400
        
        if 'data_fim' in data:
            try:
                nova_data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00'))
                if nova_data_fim != reuniao.data_fim:
                    reuniao.data_fim = nova_data_fim
                    data_fim_alterada = True
            except ValueError:
                return jsonify({'error': 'Formato de data de fim inválido'}), 400
        
        # Validar se data de fim é posterior à data de início
        if reuniao.data_fim <= reuniao.data_inicio:
            return jsonify({'error': 'Data de fim deve ser posterior à data de início'}), 400
        
        # Se as datas foram alteradas, verificar conflitos
        if data_inicio_alterada or data_fim_alterada:
            conflitos_sala = Reuniao.verificar_conflito_horario(
                reuniao.sala_id, reuniao.data_inicio, reuniao.data_fim, reuniao_id
            )
            if conflitos_sala:
                return jsonify({
                    'error': 'Conflito de horário na sala com as novas datas',
                    'conflitos': [c.titulo for c in conflitos_sala]
                }), 409
        
        # Atualizar participantes se fornecidos
        if 'participantes' in data:
            participantes_ids = data['participantes']
            participantes_indisponiveis = []
            participantes_validos = []
            
            for participante_id in participantes_ids:
                user = User.query.get(participante_id)
                if not user or not user.ativo:
                    return jsonify({'error': f'Participante com ID {participante_id} não encontrado'}), 400
                
                if not Reuniao.verificar_disponibilidade_participante(
                    participante_id, reuniao.data_inicio, reuniao.data_fim, reuniao_id
                ):
                    participantes_indisponiveis.append({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    })
                else:
                    participantes_validos.append(user)
            
            if participantes_indisponiveis:
                return jsonify({
                    'error': 'Alguns participantes não estão disponíveis no horário solicitado',
                    'participantes_indisponiveis': participantes_indisponiveis
                }), 409
            
            reuniao.participantes = participantes_validos
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reunião atualizada com sucesso',
            'reuniao': reuniao.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reuniao_bp.route('/reunioes/<int:reuniao_id>', methods=['DELETE'])
def delete_reuniao(reuniao_id):
    """Cancelar reunião (soft delete)"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        reuniao = Reuniao.query.get_or_404(reuniao_id)
        
        # Verificar se o usuário pode cancelar (criador da reunião)
        if reuniao.criador_id != session['user_id']:
            return jsonify({'error': 'Apenas o criador da reunião pode cancelá-la'}), 403
        
        # Salvar participantes antes de cancelar para enviar emails
        participantes_para_notificar = list(reuniao.participantes)
        
        reuniao.ativa = False
        db.session.commit()
        
        # Enviar notificações de cancelamento por email
        try:
            if participantes_para_notificar:
                emails_enviados = enviar_notificacao_cancelamento(reuniao, participantes_para_notificar)
                logging.info(f"Emails de cancelamento enviados: {emails_enviados}/{len(participantes_para_notificar)}")
        except Exception as e:
            logging.error(f"Erro ao enviar emails de cancelamento: {str(e)}")
            # Não falhar o cancelamento por causa do email
        
        return jsonify({'message': 'Reunião cancelada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reuniao_bp.route('/reunioes/calendario', methods=['GET'])
def get_calendario():
    """Obter reuniões para exibição em calendário"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        # Parâmetros para filtrar por mês/ano
        ano = request.args.get('ano', datetime.now().year, type=int)
        mes = request.args.get('mes', datetime.now().month, type=int)
        
        # Calcular início e fim do mês
        inicio_mes = datetime(ano, mes, 1)
        if mes == 12:
            fim_mes = datetime(ano + 1, 1, 1) - timedelta(days=1)
        else:
            fim_mes = datetime(ano, mes + 1, 1) - timedelta(days=1)
        
        reunioes = Reuniao.query.filter(
            Reuniao.ativa == True,
            Reuniao.data_inicio <= fim_mes,
            Reuniao.data_fim >= inicio_mes
        ).order_by(Reuniao.data_inicio).all()
        
        # Formatar para calendário
        eventos = []
        for reuniao in reunioes:
            eventos.append({
                'id': reuniao.id,
                'title': reuniao.titulo,
                'start': reuniao.data_inicio.isoformat(),
                'end': reuniao.data_fim.isoformat(),
                'sala': reuniao.sala_reuniao.nome,
                'participantes_count': len(reuniao.participantes),
                'criador': reuniao.criador.username
            })
        
        return jsonify(eventos), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reuniao_bp.route('/reunioes/verificar-conflito', methods=['POST'])
def verificar_conflito():
    """Verificar se há conflito de horário antes de criar/editar reunião"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        data = request.json
        sala_id = data.get('sala_id')
        data_inicio_str = data.get('data_inicio')
        data_fim_str = data.get('data_fim')
        reuniao_id = data.get('reuniao_id')  # Para edição
        participantes_ids = data.get('participantes', [])
        
        if not sala_id or not data_inicio_str or not data_fim_str:
            return jsonify({'error': 'Sala, data de início e data de fim são obrigatórios'}), 400
        
        # Converter strings para datetime
        try:
            data_inicio = datetime.fromisoformat(data_inicio_str.replace('Z', '+00:00'))
            data_fim = datetime.fromisoformat(data_fim_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Formato de data inválido'}), 400
        
        # Verificar conflitos na sala
        conflitos_sala = Reuniao.verificar_conflito_horario(sala_id, data_inicio, data_fim, reuniao_id)
        
        # Verificar disponibilidade dos participantes
        participantes_indisponiveis = []
        for participante_id in participantes_ids:
            if not Reuniao.verificar_disponibilidade_participante(participante_id, data_inicio, data_fim, reuniao_id):
                user = User.query.get(participante_id)
                if user:
                    participantes_indisponiveis.append({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    })
        
        return jsonify({
            'conflitos_sala': [{'titulo': c.titulo, 'data_inicio': c.data_inicio.isoformat(), 'data_fim': c.data_fim.isoformat()} for c in conflitos_sala],
            'participantes_indisponiveis': participantes_indisponiveis,
            'tem_conflito': len(conflitos_sala) > 0 or len(participantes_indisponiveis) > 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

