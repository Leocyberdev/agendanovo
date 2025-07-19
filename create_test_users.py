#!/usr/bin/env python3
"""
Script para criar usuários de teste no sistema de agendamento de reuniões
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import User, db
from src.models.sala import Sala
from src.main import app

def create_test_users():
    with app.app_context():
        # Verificar se já existem usuários
        if User.query.count() > 0:
            print("Usuários já existem no sistema.")
            return
        
        # Criar usuários de teste
        usuarios_teste = [
            {
                'username': 'admin',
                'email': 'admin@montereletrica.com',
                'password': '123456'
            },
            {
                'username': 'joao.silva',
                'email': 'joao.silva@montereletrica.com',
                'password': '123456'
            },
            {
                'username': 'maria.santos',
                'email': 'maria.santos@montereletrica.com',
                'password': '123456'
            },
            {
                'username': 'pedro.oliveira',
                'email': 'pedro.oliveira@montereletrica.com',
                'password': '123456'
            },
            {
                'username': 'ana.costa',
                'email': 'ana.costa@montereletrica.com',
                'password': '123456'
            }
        ]
        
        for user_data in usuarios_teste:
            user = User(
                username=user_data['username'],
                email=user_data['email']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
        
        db.session.commit()
        print(f"Criados {len(usuarios_teste)} usuários de teste:")
        for user_data in usuarios_teste:
            print(f"- {user_data['username']} ({user_data['email']}) - senha: {user_data['password']}")

if __name__ == '__main__':
    create_test_users()

