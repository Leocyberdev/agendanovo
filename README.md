# Sistema de Agendamento de Reuniões

Sistema completo de agendamento de reuniões desenvolvido em Flask com interface web responsiva, validação de conflitos de horários e notificações automáticas por email.

## 🚀 Funcionalidades Implementadas

### ✅ 1. Sistema de Autenticação
- Tela de login segura com validação
- Gerenciamento de sessões
- Controle de acesso às funcionalidades

### ✅ 2. Agendamento de Reuniões
- Formulário completo para criar reuniões
- Seleção de salas disponíveis:
  - Sala de Reunião (12 pessoas)
  - Refeitório (20 pessoas)
  - Sala de Treinamento (15 pessoas)
- Seleção de participantes com busca
- Validação de conflitos de horário (buffer de 10 minutos)
- Verificação de disponibilidade dos participantes

### ✅ 3. Menu Interativo
- Menu lateral responsivo no canto superior esquerdo
- Navegação entre as páginas:
  - Agendar Reunião
  - Calendário de Reuniões
  - Minhas Reuniões

### ✅ 4. Calendário de Reuniões
- Visualização em calendário completo
- Diferentes visualizações: Mês, Semana, Dia
- Exibição de todas as reuniões agendadas
- Interface intuitiva com FullCalendar

### ✅ 5. Notificações por Email
- **Email remetente**: agendamontereletrica@gmail.com
- **Notificação de agendamento**: Enviada automaticamente para todos os participantes
- **Notificação de cancelamento**: Enviada quando uma reunião é cancelada
- **Formato**: Emails HTML responsivos com todas as informações da reunião

### ✅ 6. Validações de Negócio
- Não permite agendar reuniões no mesmo horário na mesma sala
- Buffer de 10 minutos entre reuniões
- Verificação de disponibilidade dos participantes
- Validação de datas e horários

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Banco de Dados**: SQLite
- **Calendário**: FullCalendar.js
- **Email**: SMTP Gmail
- **Autenticação**: Flask Sessions com hash de senhas

## 📋 Usuários de Teste Criados

| Usuário | Email | Senha |
|---------|-------|-------|
| admin | admin@montereletrica.com | 123456 |
| joao.silva | joao.silva@montereletrica.com | 123456 |
| maria.santos | maria.santos@montereletrica.com | 123456 |
| pedro.oliveira | pedro.oliveira@montereletrica.com | 123456 |
| ana.costa | ana.costa@montereletrica.com | 123456 |

## 🚀 Como Executar o Sistema

### 1. Navegue até o diretório do projeto
```bash
cd agendador-reunioes
```

### 2. Ative o ambiente virtual
```bash
source venv/bin/activate
```

### 3. Execute o servidor
```bash
python src/main.py
```

### 4. Acesse o sistema
Abra seu navegador e acesse: `http://localhost:5000`

## 📁 Estrutura do Projeto

```
agendador-reunioes/
├── src/
│   ├── models/          # Modelos de dados
│   │   ├── user.py      # Modelo de usuário
│   │   ├── sala.py      # Modelo de sala
│   │   └── reuniao.py   # Modelo de reunião
│   ├── routes/          # Rotas da API
│   │   ├── auth.py      # Autenticação
│   │   ├── user.py      # Usuários
│   │   ├── sala.py      # Salas
│   │   └── reuniao.py   # Reuniões
│   ├── utils/           # Utilitários
│   │   └── email_service.py  # Serviço de email
│   ├── static/          # Arquivos estáticos
│   │   ├── index.html   # Interface principal
│   │   └── script.js    # JavaScript do frontend
│   ├── database/        # Banco de dados
│   │   └── app.db       # SQLite database
│   └── main.py          # Arquivo principal
├── venv/                # Ambiente virtual
├── requirements.txt     # Dependências
└── README.md           # Esta documentação
```

## 🔧 Configurações de Email

O sistema está configurado para enviar emails através do Gmail:
- **Servidor SMTP**: smtp.gmail.com
- **Porta**: 587
- **Email**: agendamontereletrica@gmail.com
- **Senha de App**: cent dvbi wgxc acjd

## 📧 Formato dos Emails

### Email de Agendamento
- **Assunto**: "Nova Reunião Agendada: [Título da Reunião]"
- **Conteúdo**: Detalhes completos da reunião, participantes e local
- **Formato**: HTML responsivo com design profissional

### Email de Cancelamento
- **Assunto**: "Reunião Cancelada: [Título da Reunião]"
- **Conteúdo**: Informações da reunião cancelada
- **Formato**: HTML responsivo com destaque para o cancelamento

## 🎯 Funcionalidades Específicas Implementadas

1. **Validação de Conflitos**: Sistema não permite agendar reuniões com menos de 10 minutos de diferença na mesma sala
2. **Verificação de Participantes**: Valida se cada participante está disponível no horário solicitado
3. **Interface Responsiva**: Funciona perfeitamente em desktop e mobile
4. **Menu Lateral**: Navegação intuitiva conforme solicitado
5. **Calendário Interativo**: Visualização completa das reuniões agendadas
6. **Notificações Automáticas**: Emails enviados automaticamente para todos os participantes

## 🔒 Segurança

- Senhas armazenadas com hash seguro
- Validação de sessões
- Controle de acesso às funcionalidades
- Validação de dados de entrada

## 📱 Responsividade

O sistema foi desenvolvido para funcionar perfeitamente em:
- Desktop
- Tablets
- Smartphones

## 🎨 Design

- Interface moderna com gradientes
- Cores profissionais
- Ícones FontAwesome
- Layout limpo e intuitivo
- Feedback visual para ações do usuário

## ✅ Status do Projeto

**CONCLUÍDO** - Todas as funcionalidades solicitadas foram implementadas e testadas com sucesso:

- ✅ Tela de login
- ✅ Tela de agendamento com validações
- ✅ Menu interativo no canto superior esquerdo
- ✅ Calendário de reuniões
- ✅ Notificações por email automáticas
- ✅ Validação de conflitos de horário
- ✅ Verificação de disponibilidade de participantes
- ✅ Interface responsiva e moderna

O sistema está pronto para uso em produção!

