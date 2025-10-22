# 🎓 Sistema de Notas para Escolas de Inglês

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.7-green?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

## 📋 Resumo Executivo

**Sistema de Boletins** é uma solução completa e moderna para gestão educacional em escolas de idiomas, desenvolvida em Django. O sistema oferece controle total sobre turmas, alunos, competências e notas, com funcionalidades avançadas de auditoria, analytics e administração.

### 🎯 **Objetivo**
Digitalizar e modernizar o processo de gestão de notas em escolas de inglês, proporcionando uma interface intuitiva para professores e um painel administrativo completo para coordenadores.

### 👥 **Usuários-Alvo**
- **Professores**: Lançamento rápido de notas e acompanhamento de progresso
- **Coordenadores**: Visão geral de performance e analytics detalhados  
- **Administradores**: Gestão completa do sistema e auditoria de ações

### ⚡ **Principais Diferenciais**
- **🔍 Sistema de Auditoria Completo**: Rastreamento automático de todas as ações
- **📊 Analytics Inteligentes**: 4 gráficos interativos com dados em tempo real
- **🛡️ Segurança Avançada**: Cache otimizado e headers de proteção
- **📱 Interface Responsiva**: Funciona perfeitamente em desktop e mobile
- **📁 Importação Inteligente**: Upload em lote com detecção automática de problemas

### 🚀 **Tecnologia**
Construído com **Django 5.2.7**, banco **SQLite** (facilmente migrável para PostgreSQL), frontend com **Chart.js** e **CSS3** moderno, sistema de **cache local** e **auditoria automática**.

### 📈 **Status do Projeto**
✅ **Em Produção** - Sistema estável com auditoria completa, interface unificada e performance otimizada.

---

Um sistema completo e moderno para gerenciamento de notas, turmas e competências em escolas de idiomas, desenvolvido com Django. Inclui painéis administrativos avançados, analytics inteligentes, **sistema de auditoria completo** e interface intuitiva para professores.

![Dashboard Preview](docs/dashboard-preview.png)

## ✨ Características Principais

### 🔍 **Sistema de Auditoria Avançado** ⭐ NOVO!
- **Rastreamento Completo**: Todas as ações importantes são registradas automaticamente
- **Logs de Notas**: Histórico completo de lançamentos e alterações de notas
- **Auditoria de Login**: Controle de acessos com IP e User-Agent
- **Métricas do Sistema**: Coleta automática de dados de performance
- **Interface Unificada**: Visualização de logs no painel administrativo

### 🛡️ **Segurança e Performance** ⭐ NOVO!
- **Headers de Segurança**: Proteção contra ataques comuns
- **Sistema de Cache**: Performance otimizada (5 min, 1000 entradas)
- **Localização PT-BR**: Interface completamente em português
- **Backup Automático**: Sistema preparado para backups regulares

### 🎯 **Gestão Completa de Turmas**
- **Tipos de Turma Flexíveis**: Basic 1, Basic 2, HR4, Advanced, Conversation, etc.
- **Competências Personalizáveis**: Speaking, Listening, Reading, Writing, Grammar, Vocabulary
- **Associação Automática**: Competências são automaticamente associadas aos tipos de turma
- **Controle de Alunos**: Campos expandidos com data de cadastro, status ativo e observações

### 📊 **Analytics Inteligentes**
- **4 Gráficos Interativos**: Progresso por turma, performance de professores, médias de competências, distribuição de notas
- **Dados em Tempo Real**: Estatísticas calculadas dinamicamente
- **Interface Responsiva**: Funciona perfeitamente em desktop e mobile

### 👨‍🏫 **Portal do Professor**
- **Percentuais Visuais**: Progresso de cada turma com barras coloridas
- **Status Inteligente**: Indicadores verdes/amarelos/vermelhos baseados no progresso
- **Lançamento Simplificado**: Interface intuitiva para inserção de notas
- **Logs Automáticos**: Todas as alterações de notas são registradas automaticamente

### 🔧 **Administração Avançada**
- **Importação Excel/CSV**: Upload em lote de alunos com validação inteligente
- **Gestão de Competências**: CRUD completo com validação de dependências
- **Sistema de Tipos**: Organização hierárquica de turmas e competências
- **Detecção de Problemas**: Identificação automática de duplicatas e inconsistências

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)
- Git

### 1. Clone o Repositório
```bash
git clone https://github.com/RomuloCifer/Site_boletins.git
cd Site_boletins
```

### 2. Crie um Ambiente Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o Banco de Dados
```bash
python manage.py migrate
```

### 5. Crie um Superusuário
```bash
python manage.py createsuperuser
```

### 6. (Opcional) Carregue Dados de Exemplo
```bash
python criar_dados_analytics.py
```

### 7. Execute o Servidor
```bash
python manage.py runserver
```

🎉 **Pronto!** Acesse `http://127.0.0.1:8000/admin-tools/` para começar!

## 📱 URLs Principais

| Funcionalidade | URL | Descrição |
|----------------|-----|-----------|
| **Dashboard Admin** | `/admin/` | ⭐ **Painel administrativo unificado** |
| **Analytics** | `/admin-tools/analytics/` | Gráficos e estatísticas avançadas |
| **Portal Professor** | `/portal/` | Interface para professores |
| **Logs de Auditoria** | `/admin/core/auditlog/` | ⭐ **Sistema de auditoria completo** |
| **Métricas Sistema** | `/admin/core/systemmetrics/` | ⭐ **Métricas de performance** |
| **API Analytics** | `/admin-tools/api/analytics-data/` | Endpoint JSON para gráficos |

## 🧪 Comandos Especiais

### ⭐ Testar Sistema de Auditoria
```bash
python manage.py teste_auditoria
```

### 🔧 Configurar Data Limite
```bash
python manage.py configurar_data_limite
```

### 📊 Gerar Dados de Exemplo
```bash
python criar_dados_analytics.py
```

### 🛠️ Configurar Grupos de Usuário
```bash
python setup_groups.py
```

## 🏗️ Estrutura do Projeto

```
Site_boletins/
├── 📁 core/                    # Modelos principais
│   ├── models.py              # TipoTurma, Turma, Competencia, Aluno, AuditLog, SystemMetrics
│   ├── admin.py               # Configurações do Django Admin
│   ├── logging_utils.py       # ⭐ Sistema de auditoria simplificado
│   ├── migrations/            # Migrações do banco
│   └── management/commands/   # ⭐ Comandos personalizados
├── 📁 admin_panel/            # Painel administrativo
│   ├── views.py               # Lógica de negócio e analytics
│   ├── admin_custom.py        # ⭐ Admin customizado unificado
│   ├── templates/             # Templates HTML
│   └── static/                # CSS, JS, imagens
├── 📁 teacher_portal/         # Portal dos professores
│   ├── views.py               # ⭐ Com logs automáticos
│   └── templates/             # Interface do professor
├── 📁 SistemaNotas/           # Configurações Django
│   ├── settings.py            # ⭐ Com cache e segurança
│   ├── settings_production.py # ⭐ Configurações de produção
│   └── urls.py                # Roteamento principal
├── 📁 docs/                   # ⭐ Documentação
│   ├── MELHORIAS_IMPLEMENTADAS.md
│   ├── EXPLICACAO_ADMIN.md
│   └── COMMIT_DESCRIPTION.md
├── requirements.txt           # Dependências Python
├── manage.py                  # Comandos Django
└── README.md                  # Este arquivo
```

## 🎨 Tecnologias Utilizadas

### Backend
- **Django 5.2.7**: Framework web robusto
- **SQLite**: Banco de dados (fácil migração para PostgreSQL)
- **Pandas**: Processamento de arquivos Excel/CSV
- **Sistema de Cache**: ⭐ Local memory cache otimizado
- **Sistema de Auditoria**: ⭐ Logs automáticos e rastreamento

### Frontend
- **Chart.js**: Gráficos interativos e responsivos
- **CSS3**: Gradientes, animações e design moderno
- **HTML5**: Estrutura semântica
- **JavaScript**: Interatividade e AJAX

### Segurança e Performance
- **Headers de Segurança**: ⭐ Proteção contra ataques
- **Cache Inteligente**: ⭐ 5 minutos, 1000 entradas
- **Auditoria Completa**: ⭐ Rastreamento de todas as ações
- **Localização PT-BR**: ⭐ Interface em português

### Ferramentas
- **openpyxl**: Leitura de arquivos Excel
- **Pillow**: Manipulação de imagens
- **python-decouple**: Gerenciamento de variáveis de ambiente

## 📊 Funcionalidades Detalhadas

### Sistema de Tipos de Turma
```python
# Exemplo de tipos disponíveis
Basic 1     → Speaking, Listening, Reading, Writing
Basic 2     → + Grammar
HR4         → Todas as competências
Advanced    → Competências avançadas
Conversation → Speaking, Listening
```

### Notas Flexíveis
- **Numéricas (0-100)**: Para Speaking, Listening, Reading, Writing
- **Categóricas (A,B,C,D)**: Para Grammar, Vocabulary
- **Validação Automática**: Previne dados inconsistentes

### Analytics Disponíveis
1. **📈 Progresso por Tipo de Turma**: Barras coloridas mostrando % de completude
2. **👥 Performance dos Professores**: Ranking horizontal de produtividade
3. **📚 Médias das Competências**: Gráfico de linha com tendências
4. **🥧 Distribuição Categórica**: Pizza chart para notas A,B,C,D

## 🔧 Guia de Uso

### Para Administradores

#### 1. **Acesso ao Sistema** ⭐ NOVO!
1. Acesse `/admin/` (interface unificada)
2. Veja o dashboard com estatísticas em tempo real
3. Monitore logs de auditoria em **"Audit logs"**
4. Verifique métricas do sistema em **"System metrics"**

#### 2. **Configuração Inicial**
1. Vá em **"Tipos de Turma"** → Crie os tipos necessários
2. Associe competências a cada tipo
3. Em **"Gerenciar Competências"** → Configure as avaliações
4. Configure data limite em **"Configuração Sistema"**

#### 3. **Importação de Alunos**
1. Clique em **"Importar Alunos"**
2. Faça upload de arquivo CSV/Excel com colunas:
   ```csv
   nome_completo,identificador_turma,matricula
   João Silva,Basic1-MW18,2024001
   Maria Santos,HR4-TT20,2024002
   ```
3. Selecione modo: turma específica ou lote
4. Confirme a importação (logs automáticos gerados)

#### 4. **Monitoramento e Auditoria** ⭐ NOVO!
1. **Logs de Auditoria**: Veja todas as ações dos usuários
2. **Métricas**: Monitore performance do sistema
3. **Detecção de Problemas**: Identificação automática de duplicatas
4. **Teste de Auditoria**: Execute `python manage.py teste_auditoria`

### Para Professores

#### 1. **Acesso ao Portal**
1. Acesse `/portal/`
2. Faça login com suas credenciais
3. Visualize suas turmas no dashboard

#### 2. **Lançamento de Notas** ⭐ MELHORADO!
1. Clique na turma desejada
2. Selecione o aluno
3. Escolha a competência
4. Insira a nota (numérica ou categórica)
5. Salve (ação automaticamente registrada nos logs)
5. Salve

#### 3. **Acompanhamento**
- **Barras de Progresso**: Verde (>80%), Amarelo (50-80%), Vermelho (<50%)
- **Estatísticas**: Veja quantos alunos têm notas completas
- **Status Visual**: Indicadores claros de progresso

## 🔐 Sistema de Permissões

### Grupos Recomendados

#### 👑 **Administradores**
- Acesso completo ao sistema
- Gestão de usuários e permissões
- Analytics completos
- Configuração de tipos e competências

#### 👨‍🏫 **Professores**
- Ver apenas suas turmas
- Lançar e editar notas dos seus alunos
- Relatórios básicos de progresso
- Sem acesso a configurações globais

#### 📊 **Coordenadores**
- Visualizar analytics de todas as turmas
- Relatórios avançados
- Sem permissão para deletar dados
- Monitoramento de performance

## 🚀 Deploy em Produção

### Preparação
```bash
# 1. Configure variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 2. Configure banco PostgreSQL (recomendado)
pip install psycopg2-binary

# 3. Colete arquivos estáticos
python manage.py collectstatic

# 4. Execute migrações
python manage.py migrate --settings=SistemaNotas.settings_production
```

### Opções de Deploy
- **Heroku**: Deploy rápido com integração Git
- **DigitalOcean**: Droplets com Docker
- **AWS**: EC2 com RDS para banco
- **VPS**: Servidor dedicado com nginx + gunicorn

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um **Pull Request**

### Padrões de Código
- Siga as convenções do Django
- Use **black** para formatação: `black .`
- Documente funções complexas
- Escreva testes para novas funcionalidades

## 📝 Roadmap

### 🔜 Próximas Funcionalidades
- [ ] **API REST Completa**: Endpoints para integração externa
- [ ] **Relatórios PDF**: Exportação de boletins em PDF
- [ ] **Notificações**: Sistema de alertas por email
- [ ] **App Mobile**: Aplicativo React Native
- [ ] **Dashboard Pais**: Portal para responsáveis
- [x] **Sistema de Auditoria**: ⭐ **IMPLEMENTADO!**
- [x] **Cache Otimizado**: ⭐ **IMPLEMENTADO!**
- [x] **Segurança Avançada**: ⭐ **IMPLEMENTADO!**

### 🎯 Melhorias Planejadas
- [ ] **Testes Automatizados**: Cobertura >90%
- [ ] **Docker**: Containerização completa
- [ ] **CI/CD**: Pipeline de deploy automático
- [ ] **Monitoramento**: Logs e métricas avançadas
- [ ] **Multi-idiomas**: Internacionalização (i18n)
- [x] **Backup Sistema**: ⭐ **PREPARADO!**
- [x] **Interface Unificada**: ⭐ **IMPLEMENTADO!**

## 🔍 Sistema de Auditoria ⭐ NOVO!

### Funcionalidades de Auditoria
- **Rastreamento Automático**: Todas as ações são logadas
- **Logs de Notas**: Histórico de criação/edição de notas
- **Auditoria de Login**: Controle de acessos e IPs
- **Métricas do Sistema**: Performance e uso
- **Interface Admin**: Visualização unificada dos logs

### Como Usar
```bash
# Testar sistema de auditoria
python manage.py teste_auditoria

# Visualizar logs
# Acesse: http://127.0.0.1:8000/admin/core/auditlog/

# Verificar métricas
# Acesse: http://127.0.0.1:8000/admin/core/systemmetrics/
```

### Tipos de Log
- **LOGIN**: Tentativas de acesso (sucesso/falha)
- **CREATE/UPDATE**: Criação e edição de notas
- **IMPORT**: Importação de alunos
- **ERROR**: Erros do sistema
- **CUSTOM**: Ações personalizadas

## 🛡️ Segurança e Performance ⭐ NOVO!

### Configurações de Segurança
- **Headers de Proteção**: X-Frame-Options, X-Content-Type-Options
- **Cache Inteligente**: 5 minutos, 1000 entradas máx
- **Logs de IP**: Rastreamento de origem das ações
- **Fallback de Logs**: Sistema não falha se auditoria der erro

### Performance
- **Cache Local**: Reduz consultas ao banco
- **Índices Otimizados**: Consultas de auditoria rápidas
- **Queries Eficientes**: Otimização de N+1 queries

## 🐛 Suporte

### Problemas Comuns

#### Erro de Migração
```bash
# Aplicar migrações pendentes
python manage.py migrate

# Se persistir, resetar (CUIDADO: perde dados!)
rm db.sqlite3
rm -rf core/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

#### Sistema de Auditoria ⭐ NOVO!
```bash
# Testar se auditoria está funcionando
python manage.py teste_auditoria

# Verificar logs de erro
python manage.py shell
>>> from core.models import AuditLog
>>> AuditLog.objects.filter(acao='ERROR').order_by('-timestamp')[:5]
```

#### Cache Issues
```bash
# Limpar cache manualmente
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Contato
- **GitHub Issues**: [Reportar bugs](https://github.com/RomuloCifer/Site_boletins/issues)
- **Email**: romulocifer@gmail.com
- **Documentação**: Consulte os arquivos em `/docs/`

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## ⭐ Changelog Recente

### v2.0.0 - Sistema de Auditoria (22/10/2025)
- ✅ **Sistema de auditoria completo** com rastreamento de todas as ações
- ✅ **Interface admin unificada** com logs integrados
- ✅ **Cache otimizado** para melhor performance
- ✅ **Configurações de segurança** aprimoradas
- ✅ **Localização PT-BR** completa
- ✅ **Modelo Aluno expandido** com novos campos
- ✅ **Comando de teste** para validação do sistema
- ✅ **Documentação completa** das melhorias

### v1.0.0 - Versão Inicial
- ✅ Sistema básico de notas e turmas
- ✅ Portal do professor funcional
- ✅ Analytics com 4 gráficos
- ✅ Importação de alunos CSV/Excel
- ✅ Gestão de competências

---

**🎯 Sistema de Boletins - Desenvolvido com ❤️ usando Django**
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

#### Permissões
- Verifique se o usuário tem `is_staff=True`
- Configure grupos apropriados no Django Admin

### Reportar Bugs
Abra uma [issue](https://github.com/RomuloCifer/Site_boletins/issues) com:
- Descrição detalhada do problema
- Steps para reproduzir
- Screenshots (se aplicável)
- Versão do Python e Django

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👏 Agradecimentos

- **Django Community**: Framework excepcional
- **Chart.js**: Biblioteca de gráficos fantástica
- **Bootstrap**: Inspiração para UI/UX
- **Pandas**: Processamento de dados eficiente

## 📞 Contato

**Desenvolvedor**: RomuloCifer  
**Email**: [seu-email@exemplo.com](ciferomulo@gmail.com )  
**GitHub**: [@RomuloCifer](https://github.com/RomuloCifer)  
**LinkedIn**: [Seu LinkedIn](https://www.linkedin.com/in/romulo-portugal-070781363)

---

<div align="center">

**⭐ Se este projeto foi útil, deixe uma estrela! ⭐**

![Footer](docs/footer-banner.png)

*Desenvolvido com ❤️ para educadores e estudantes*

</div>