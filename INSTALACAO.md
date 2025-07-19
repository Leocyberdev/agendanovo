# Guia de Instalação - Sistema de Agendamento de Reuniões

## 📋 Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno

## 🔧 Instalação Passo a Passo

### 1. Preparação do Ambiente

```bash
# Clone ou copie o projeto para seu servidor
# Navegue até o diretório do projeto
cd agendador-reunioes
```

### 2. Ativação do Ambiente Virtual

```bash
# Ative o ambiente virtual (já configurado)
source venv/bin/activate
```

### 3. Verificação das Dependências

```bash
# Verifique se todas as dependências estão instaladas
pip list

# Se necessário, instale dependências adicionais
pip install flask flask-cors flask-sqlalchemy werkzeug
```

### 4. Configuração do Banco de Dados

O banco de dados SQLite já está configurado e será criado automaticamente na primeira execução.

### 5. Execução do Sistema

```bash
# Execute o servidor Flask
python src/main.py
```

O sistema estará disponível em: `http://localhost:5000`

## 🌐 Configuração para Produção

### Opção 1: Servidor Local
Para usar em rede local, o sistema já está configurado para aceitar conexões de qualquer IP (0.0.0.0).

### Opção 2: Deploy em Servidor Web
Para deploy em produção, considere usar:
- **Gunicorn** como servidor WSGI
- **Nginx** como proxy reverso
- **SSL/HTTPS** para segurança

Exemplo com Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

## 📧 Configuração de Email

O sistema está configurado para usar Gmail SMTP:
- **Email**: agendamontereletrica@gmail.com
- **Senha de App**: cent dvbi wgxc acjd

### Para Alterar as Configurações de Email:
Edite o arquivo `src/utils/email_service.py`:

```python
EMAIL_HOST = 'smtp.gmail.com'  # Servidor SMTP
EMAIL_PORT = 587               # Porta
EMAIL_USER = 'seu-email@gmail.com'  # Seu email
EMAIL_PASSWORD = 'sua-senha-app'     # Senha de app
```

## 👥 Gerenciamento de Usuários

### Usuários Pré-cadastrados:
- **admin** / 123456
- **joao.silva** / 123456
- **maria.santos** / 123456
- **pedro.oliveira** / 123456
- **ana.costa** / 123456

### Para Adicionar Novos Usuários:
1. Acesse o sistema como admin
2. Use a API ou adicione diretamente no banco:

```python
# Exemplo de script para adicionar usuário
from src.models.user import User, db
from src.main import app

with app.app_context():
    user = User(username='novo.usuario', email='novo@empresa.com')
    user.set_password('senha123')
    db.session.add(user)
    db.session.commit()
```

## 🏢 Configuração de Salas

As salas padrão são criadas automaticamente:
- Sala de Reunião (12 pessoas)
- Refeitório (20 pessoas)
- Sala de Treinamento (15 pessoas)

### Para Adicionar/Modificar Salas:
Edite o arquivo `src/main.py` na seção de criação de salas padrão.

## 🔒 Configurações de Segurança

### Alterar Chave Secreta:
No arquivo `src/main.py`, altere:
```python
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
```

### Configurar HTTPS:
Para produção, configure SSL/TLS no seu servidor web.

## 📱 Acesso Mobile

O sistema é totalmente responsivo e funciona em:
- Smartphones
- Tablets
- Desktops

## 🔧 Manutenção

### Backup do Banco de Dados:
```bash
cp src/database/app.db backup_$(date +%Y%m%d).db
```

### Logs do Sistema:
Os logs são exibidos no console. Para produção, configure logging em arquivo:

```python
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)
```

## ❓ Solução de Problemas

### Problema: Erro de importação
**Solução**: Verifique se o ambiente virtual está ativado

### Problema: Emails não são enviados
**Solução**: 
1. Verifique as configurações SMTP
2. Confirme se a senha de app está correta
3. Verifique se o Gmail permite apps menos seguros

### Problema: Banco de dados corrompido
**Solução**: 
```bash
rm src/database/app.db
python src/main.py  # Recria o banco
python create_test_users.py  # Recria usuários
```

### Problema: Porta 5000 em uso
**Solução**: Altere a porta no arquivo `src/main.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique este guia de instalação
2. Consulte o README.md
3. Verifique os logs do sistema
4. Teste com usuários de exemplo

## ✅ Checklist de Instalação

- [ ] Python 3.11+ instalado
- [ ] Projeto copiado para o servidor
- [ ] Ambiente virtual ativado
- [ ] Dependências verificadas
- [ ] Sistema executado com sucesso
- [ ] Acesso via navegador funcionando
- [ ] Login testado com usuários de exemplo
- [ ] Configurações de email verificadas
- [ ] Sistema testado em diferentes dispositivos

**Sistema pronto para uso!** 🎉

