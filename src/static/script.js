// Estado global da aplicação
let currentUser = null;
let salas = [];
let usuarios = [];
let participantesSelecionados = [];
let calendar = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    setupEventListeners();
});

// Verificar autenticação
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/check');
        const data = await response.json();
        
        if (data.authenticated) {
            currentUser = data.user;
            showMainApp();
        } else {
            showLoginScreen();
        }
    } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        showLoginScreen();
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Agendamento form
    document.getElementById('agendamentoForm').addEventListener('submit', handleAgendamento);
    
    // Overlay click
    document.getElementById('overlay').addEventListener('click', closeSidebar);
}

// Manipular login
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('loginBtn');
    
    loginBtn.disabled = true;
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Entrando...';
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            showAlert('loginAlert', 'Login realizado com sucesso!', 'success');
            setTimeout(() => {
                showMainApp();
            }, 1000);
        } else {
            showAlert('loginAlert', data.error || 'Erro ao fazer login', 'error');
        }
    } catch (error) {
        showAlert('loginAlert', 'Erro de conexão. Tente novamente.', 'error');
    } finally {
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Entrar';
    }
}

// Logout
async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        currentUser = null;
        showLoginScreen();
    } catch (error) {
        console.error('Erro ao fazer logout:', error);
        showLoginScreen();
    }
}

// Mostrar tela de login
function showLoginScreen() {
    document.getElementById('loginScreen').classList.remove('hidden');
    document.getElementById('mainApp').classList.add('hidden');
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    document.getElementById('loginAlert').innerHTML = '';
}

// Mostrar aplicação principal
async function showMainApp() {
    document.getElementById('loginScreen').classList.add('hidden');
    document.getElementById('mainApp').classList.remove('hidden');
    
    // Atualizar informações do usuário
    document.getElementById('userWelcome').textContent = `Bem-vindo, ${currentUser.username}!`;
    
    // Carregar dados iniciais
    await loadInitialData();
    
    // Mostrar página de agendamento por padrão
    showPage('agendamento');
}

// Carregar dados iniciais
async function loadInitialData() {
    try {
        // Carregar salas
        const salasResponse = await fetch('/api/salas');
        if (salasResponse.ok) {
            salas = await salasResponse.json();
            populateSalasSelect();
        }
        
        // Carregar usuários
        const usuariosResponse = await fetch('/api/users');
        if (usuariosResponse.ok) {
            usuarios = await usuariosResponse.json();
            populateUsuariosSelect();
        }
    } catch (error) {
        console.error('Erro ao carregar dados iniciais:', error);
    }
}

// Popular select de salas
function populateSalasSelect() {
    const select = document.getElementById('sala');
    select.innerHTML = '<option value="">Selecione uma sala</option>';
    
    salas.forEach(sala => {
        const option = document.createElement('option');
        option.value = sala.id;
        option.textContent = `${sala.nome} (${sala.capacidade} pessoas)`;
        select.appendChild(option);
    });
}

// Popular select de usuários
function populateUsuariosSelect() {
    const select = document.getElementById('participanteSelect');
    select.innerHTML = '<option value="">Selecione um participante</option>';
    
    usuarios.forEach(usuario => {
        if (usuario.id !== currentUser.id) { // Não incluir o usuário atual
            const option = document.createElement('option');
            option.value = usuario.id;
            option.textContent = `${usuario.username} (${usuario.email})`;
            select.appendChild(option);
        }
    });
}

// Adicionar participante
function adicionarParticipante() {
    const select = document.getElementById('participanteSelect');
    const selectedId = parseInt(select.value);
    
    if (!selectedId) {
        showAlert('agendamentoAlert', 'Selecione um participante', 'warning');
        return;
    }
    
    // Verificar se já foi adicionado
    if (participantesSelecionados.find(p => p.id === selectedId)) {
        showAlert('agendamentoAlert', 'Participante já foi adicionado', 'warning');
        return;
    }
    
    const usuario = usuarios.find(u => u.id === selectedId);
    if (usuario) {
        participantesSelecionados.push(usuario);
        updateParticipantesList();
        select.value = '';
    }
}

// Remover participante
function removerParticipante(userId) {
    participantesSelecionados = participantesSelecionados.filter(p => p.id !== userId);
    updateParticipantesList();
}

// Atualizar lista de participantes
function updateParticipantesList() {
    const container = document.getElementById('participantesList');
    
    if (participantesSelecionados.length === 0) {
        container.innerHTML = '<p style="color: #666; font-style: italic;">Nenhum participante selecionado</p>';
        return;
    }
    
    container.innerHTML = participantesSelecionados.map(participante => `
        <div class="participante-item">
            <span><i class="fas fa-user"></i> ${participante.username} (${participante.email})</span>
            <button type="button" class="remove-participante" onclick="removerParticipante(${participante.id})">
                <i class="fas fa-times"></i> Remover
            </button>
        </div>
    `).join('');
}

// Manipular agendamento
async function handleAgendamento(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const agendarBtn = document.getElementById('agendarBtn');
    
    // Validar datas
    const dataInicio = new Date(formData.get('dataInicio'));
    const dataFim = new Date(formData.get('dataFim'));
    
    if (dataFim <= dataInicio) {
        showAlert('agendamentoAlert', 'A data de término deve ser posterior à data de início', 'error');
        return;
    }
    
    // Verificar se é no futuro
    const agora = new Date();
    if (dataInicio <= agora) {
        showAlert('agendamentoAlert', 'A reunião deve ser agendada para o futuro', 'error');
        return;
    }
    
    agendarBtn.disabled = true;
    agendarBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Agendando...';
    
    try {
        const reuniaoData = {
            titulo: formData.get('titulo'),
            descricao: formData.get('descricao'),
            data_inicio: dataInicio.toISOString(),
            data_fim: dataFim.toISOString(),
            sala_id: parseInt(formData.get('sala')),
            participantes: participantesSelecionados.map(p => p.id)
        };
        
        const response = await fetch('/api/reunioes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(reuniaoData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('agendamentoAlert', 'Reunião agendada com sucesso!', 'success');
            document.getElementById('agendamentoForm').reset();
            participantesSelecionados = [];
            updateParticipantesList();
            
            // Atualizar calendário se estiver carregado
            if (calendar) {
                calendar.refetchEvents();
            }
        } else {
            if (response.status === 409) {
                // Conflito de horário
                let errorMsg = data.error;
                if (data.conflitos) {
                    errorMsg += '\\n\\nReuniões em conflito:';
                    data.conflitos.forEach(conflito => {
                        errorMsg += `\\n- ${conflito.titulo} (${new Date(conflito.data_inicio).toLocaleString()} - ${new Date(conflito.data_fim).toLocaleString()})`;
                    });
                }
                if (data.participantes_indisponiveis) {
                    errorMsg += '\\n\\nParticipantes indisponíveis:';
                    data.participantes_indisponiveis.forEach(p => {
                        errorMsg += `\\n- ${p.username}`;
                    });
                }
                showAlert('agendamentoAlert', errorMsg, 'error');
            } else {
                showAlert('agendamentoAlert', data.error || 'Erro ao agendar reunião', 'error');
            }
        }
    } catch (error) {
        showAlert('agendamentoAlert', 'Erro de conexão. Tente novamente.', 'error');
    } finally {
        agendarBtn.disabled = false;
        agendarBtn.innerHTML = '<i class="fas fa-calendar-plus"></i> Agendar Reunião';
    }
}

// Mostrar página
function showPage(pageName) {
    // Esconder todas as páginas
    document.querySelectorAll('.main-content').forEach(page => {
        page.classList.add('hidden');
    });
    
    // Remover classe active de todos os links do menu
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        link.classList.remove('active');
    });
    
    // Mostrar página selecionada
    document.getElementById(pageName + 'Page').classList.remove('hidden');
    
    // Adicionar classe active ao link correspondente
    event.target.classList.add('active');
    
    // Carregar conteúdo específico da página
    switch(pageName) {
        case 'calendario':
            loadCalendar();
            break;
        case 'minhas-reunioes':
            loadMinhasReunioes();
            break;
    }
    
    // Fechar sidebar em mobile
    closeSidebar();
}

// Carregar calendário
function loadCalendar() {
    if (calendar) {
        calendar.destroy();
    }
    
    const calendarEl = document.getElementById('calendar');
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'pt-br',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        buttonText: {
            today: 'Hoje',
            month: 'Mês',
            week: 'Semana',
            day: 'Dia'
        },
        events: async function(info, successCallback, failureCallback) {
            try {
                const response = await fetch(`/api/reunioes/calendario?ano=${info.start.getFullYear()}&mes=${info.start.getMonth() + 1}`);
                if (response.ok) {
                    const eventos = await response.json();
                    successCallback(eventos.map(evento => ({
                        id: evento.id,
                        title: evento.title,
                        start: evento.start,
                        end: evento.end,
                        extendedProps: {
                            sala: evento.sala,
                            participantes_count: evento.participantes_count,
                            criador: evento.criador
                        }
                    })));
                } else {
                    failureCallback('Erro ao carregar eventos');
                }
            } catch (error) {
                failureCallback(error);
            }
        },
        eventClick: function(info) {
            showEventDetails(info.event);
        },
        eventMouseEnter: function(info) {
            // Tooltip com informações da reunião
            info.el.title = `Sala: ${info.event.extendedProps.sala}\\nParticipantes: ${info.event.extendedProps.participantes_count}\\nCriador: ${info.event.extendedProps.criador}`;
        }
    });
    
    calendar.render();
}

// Mostrar detalhes do evento
async function showEventDetails(event) {
    try {
        const response = await fetch(`/api/reunioes/${event.id}`);
        if (response.ok) {
            const reuniao = await response.json();
            
            const participantesList = reuniao.participantes.map(p => p.username).join(', ');
            
            alert(`Detalhes da Reunião:
            
Título: ${reuniao.titulo}
Descrição: ${reuniao.descricao || 'Sem descrição'}
Sala: ${reuniao.sala_nome}
Início: ${new Date(reuniao.data_inicio).toLocaleString()}
Fim: ${new Date(reuniao.data_fim).toLocaleString()}
Criador: ${reuniao.criador_nome}
Participantes: ${participantesList || 'Nenhum participante'}`);
        }
    } catch (error) {
        console.error('Erro ao carregar detalhes da reunião:', error);
    }
}

// Carregar minhas reuniões
async function loadMinhasReunioes() {
    const container = document.getElementById('reunioesList');
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Carregando reuniões...</p></div>';
    
    try {
        const response = await fetch('/api/reunioes');
        if (response.ok) {
            const reunioes = await response.json();
            
            // Filtrar reuniões do usuário atual (criadas ou participando)
            const minhasReunioes = reunioes.filter(r => 
                r.criador_id === currentUser.id || 
                r.participantes.some(p => p.id === currentUser.id)
            );
            
            if (minhasReunioes.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #666; font-style: italic;">Você não tem reuniões agendadas.</p>';
                return;
            }
            
            // Separar reuniões futuras e passadas
            const agora = new Date();
            const futuras = minhasReunioes.filter(r => new Date(r.data_inicio) > agora);
            const passadas = minhasReunioes.filter(r => new Date(r.data_inicio) <= agora);
            
            let html = '';
            
            if (futuras.length > 0) {
                html += '<h3><i class="fas fa-clock"></i> Próximas Reuniões</h3>';
                html += futuras.map(reuniao => createReuniaoCard(reuniao, true)).join('');
            }
            
            if (passadas.length > 0) {
                html += '<h3 style="margin-top: 30px;"><i class="fas fa-history"></i> Reuniões Passadas</h3>';
                html += passadas.map(reuniao => createReuniaoCard(reuniao, false)).join('');
            }
            
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p style="text-align: center; color: #dc3545;">Erro ao carregar reuniões.</p>';
        }
    } catch (error) {
        container.innerHTML = '<p style="text-align: center; color: #dc3545;">Erro de conexão.</p>';
    }
}

// Criar card de reunião
function createReuniaoCard(reuniao, isFutura) {
    const dataInicio = new Date(reuniao.data_inicio);
    const dataFim = new Date(reuniao.data_fim);
    const isCreator = reuniao.criador_id === currentUser.id;
    
    return `
        <div class="reuniao-card" style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 15px; background: ${isFutura ? '#f8f9fa' : '#f5f5f5'};">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                <h4 style="margin: 0; color: #333;">${reuniao.titulo}</h4>
                ${isCreator && isFutura ? `<button onclick="cancelarReuniao(${reuniao.id})" style="background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 12px;"><i class="fas fa-times"></i> Cancelar</button>` : ''}
            </div>
            <p style="margin: 5px 0; color: #666;"><i class="fas fa-map-marker-alt"></i> ${reuniao.sala_nome}</p>
            <p style="margin: 5px 0; color: #666;"><i class="fas fa-clock"></i> ${dataInicio.toLocaleString()} - ${dataFim.toLocaleString()}</p>
            <p style="margin: 5px 0; color: #666;"><i class="fas fa-user"></i> Criado por: ${reuniao.criador_nome}</p>
            ${reuniao.participantes.length > 0 ? `<p style="margin: 5px 0; color: #666;"><i class="fas fa-users"></i> Participantes: ${reuniao.participantes.map(p => p.username).join(', ')}</p>` : ''}
            ${reuniao.descricao ? `<p style="margin: 10px 0 0 0; color: #333;">${reuniao.descricao}</p>` : ''}
        </div>
    `;
}

// Cancelar reunião
async function cancelarReuniao(reuniaoId) {
    if (!confirm('Tem certeza que deseja cancelar esta reunião?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/reunioes/${reuniaoId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Reunião cancelada com sucesso!');
            loadMinhasReunioes(); // Recarregar lista
            if (calendar) {
                calendar.refetchEvents(); // Atualizar calendário
            }
        } else {
            const data = await response.json();
            alert(data.error || 'Erro ao cancelar reunião');
        }
    } catch (error) {
        alert('Erro de conexão. Tente novamente.');
    }
}

// Toggle sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}

// Fechar sidebar
function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
}

// Mostrar alerta
function showAlert(containerId, message, type) {
    const container = document.getElementById(containerId);
    const alertClass = type === 'success' ? 'alert-success' : type === 'error' ? 'alert-error' : 'alert-warning';
    
    container.innerHTML = `
        <div class="alert ${alertClass}">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'exclamation-triangle'}"></i>
            ${message.replace(/\\n/g, '<br>')}
        </div>
    `;
    
    // Auto-hide success messages
    if (type === 'success') {
        setTimeout(() => {
            container.innerHTML = '';
        }, 5000);
    }
}

