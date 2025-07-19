from src.models.user import db

class Sala(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    capacidade = db.Column(db.Integer, nullable=False, default=10)
    ativa = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relacionamento com reuniões
    reunioes = db.relationship('Reuniao', backref='sala_reuniao', lazy=True)

    def __repr__(self):
        return f'<Sala {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'capacidade': self.capacidade,
            'ativa': self.ativa
        }

