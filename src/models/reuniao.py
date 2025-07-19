from datetime import datetime, timedelta
from src.models.user import db

# Tabela de associação para participantes da reunião
participantes_reuniao = db.Table('participantes_reuniao',
    db.Column('reuniao_id', db.Integer, db.ForeignKey('reuniao.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class Reuniao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ativa = db.Column(db.Boolean, nullable=False, default=True)
    
    # Chaves estrangeiras
    sala_id = db.Column(db.Integer, db.ForeignKey('sala.id'), nullable=False)
    criador_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relacionamentos
    criador = db.relationship('User', foreign_keys=[criador_id], backref='reunioes_criadas')
    participantes = db.relationship('User', secondary=participantes_reuniao, 
                                  backref=db.backref('reunioes_participando', lazy='dynamic'))

    def __repr__(self):
        return f'<Reuniao {self.titulo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'ativa': self.ativa,
            'sala_id': self.sala_id,
            'sala_nome': self.sala_reuniao.nome if self.sala_reuniao else None,
            'criador_id': self.criador_id,
            'criador_nome': self.criador.username if self.criador else None,
            'participantes': [{'id': p.id, 'username': p.username, 'email': p.email} for p in self.participantes]
        }

    @staticmethod
    def verificar_conflito_horario(sala_id, data_inicio, data_fim, reuniao_id=None):
        """
        Verifica se há conflito de horário para uma sala específica.
        Considera um buffer de 10 minutos antes e depois de cada reunião.
        """
        buffer = timedelta(minutes=10)
        inicio_com_buffer = data_inicio - buffer
        fim_com_buffer = data_fim + buffer
        
        query = Reuniao.query.filter(
            Reuniao.sala_id == sala_id,
            Reuniao.ativa == True,
            db.or_(
                # Nova reunião começa durante uma existente (com buffer)
                db.and_(inicio_com_buffer < Reuniao.data_fim, data_inicio < Reuniao.data_fim),
                # Nova reunião termina durante uma existente (com buffer)
                db.and__(data_fim > Reuniao.data_inicio, fim_com_buffer > Reuniao.data_inicio),
                # Nova reunião engloba uma existente
                db.and__(data_inicio <= Reuniao.data_inicio, data_fim >= Reuniao.data_fim)
            )
        )
        
        # Se estamos editando uma reunião, excluir ela da verificação
        if reuniao_id:
            query = query.filter(Reuniao.id != reuniao_id)
            
        conflitos = query.all()
        return conflitos

    @staticmethod
    def verificar_disponibilidade_participante(user_id, data_inicio, data_fim, reuniao_id=None):
        """
        Verifica se um participante está disponível no horário solicitado.
        """
        query = db.session.query(Reuniao).join(participantes_reuniao).filter(
            participantes_reuniao.c.user_id == user_id,
            Reuniao.ativa == True,
            db.or_(
                # Nova reunião começa durante uma existente
                db.and__(data_inicio < Reuniao.data_fim, data_inicio >= Reuniao.data_inicio),
                # Nova reunião termina durante uma existente
                db.and__(data_fim > Reuniao.data_inicio, data_fim <= Reuniao.data_fim),
                # Nova reunião engloba uma existente
                db.and__(data_inicio <= Reuniao.data_inicio, data_fim >= Reuniao.data_fim)
            )
        )
        
        # Se estamos editando uma reunião, excluir ela da verificação
        if reuniao_id:
            query = query.filter(Reuniao.id != reuniao_id)
            
        conflitos = query.all()
        return len(conflitos) == 0

