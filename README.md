# 🎓 Sistema de Notas para Escolas de Inglês

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.7-green?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

Um sistema completo e moderno para gerenciamento de notas, turmas e competências em escolas de idiomas, desenvolvido com Django. Inclui painéis administrativos avançados, analytics inteligentes e interface intuitiva para professores.

![Dashboard Preview](docs/dashboard-preview.png)

## ✨ Características Principais

### 🎯 **Gestão Completa de Turmas**
- **Tipos de Turma Flexíveis**: Basic 1, Basic 2, HR4, Advanced, Conversation, etc.
- **Competências Personalizáveis**: Speaking, Listening, Reading, Writing, Grammar, Vocabulary
- **Associação Automática**: Competências são automaticamente associadas aos tipos de turma

### 📊 **Analytics Inteligentes**
- **4 Gráficos Interativos**: Progresso por turma, performance de professores, médias de competências, distribuição de notas
- **Dados em Tempo Real**: Estatísticas calculadas dinamicamente
- **Interface Responsiva**: Funciona perfeitamente em desktop e mobile

### 👨‍🏫 **Portal do Professor**
- **Percentuais Visuais**: Progresso de cada turma com barras coloridas
- **Status Inteligente**: Indicadores verdes/amarelos/vermelhos baseados no progresso
- **Lançamento Simplificado**: Interface intuitiva para inserção de notas

### 🔧 **Administração Avançada**
- **Importação Excel/CSV**: Upload em lote de alunos com validação inteligente
- **Gestão de Competências**: CRUD completo com validação de dependências
- **Sistema de Tipos**: Organização hierárquica de turmas e competências

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
| **Dashboard Admin** | `/admin-tools/` | Painel administrativo principal |
| **Analytics** | `/admin-tools/analytics/` | Gráficos e estatísticas avançadas |
| **Portal Professor** | `/portal/` | Interface para professores |
| **Django Admin** | `/admin/` | Administração nativa do Django |
| **API Analytics** | `/admin-tools/api/analytics-data/` | Endpoint JSON para gráficos |

## 🏗️ Estrutura do Projeto

```
Site_boletins/
├── 📁 core/                    # Modelos principais
│   ├── models.py              # TipoTurma, Turma, Competencia, Aluno, etc.
│   ├── admin.py               # Configurações do Django Admin
│   └── migrations/            # Migrações do banco
├── 📁 admin_panel/            # Painel administrativo
│   ├── views.py               # Lógica de negócio e analytics
│   ├── templates/             # Templates HTML
│   └── static/                # CSS, JS, imagens
├── 📁 teacher_portal/         # Portal dos professores
│   ├── views.py               # Funcionalidades do professor
│   └── templates/             # Interface do professor
├── 📁 SistemaNotas/           # Configurações Django
│   ├── settings.py            # Configurações do projeto
│   └── urls.py                # Roteamento principal
├── requirements.txt           # Dependências Python
├── manage.py                  # Comandos Django
└── README.md                  # Este arquivo
```

## 🎨 Tecnologias Utilizadas

### Backend
- **Django 5.2.7**: Framework web robusto
- **SQLite**: Banco de dados (fácil migração para PostgreSQL)
- **Pandas**: Processamento de arquivos Excel/CSV
- **Django REST Framework**: APIs JSON

### Frontend
- **Chart.js**: Gráficos interativos e responsivos
- **CSS3**: Gradientes, animações e design moderno
- **HTML5**: Estrutura semântica
- **JavaScript**: Interatividade e AJAX

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

#### 1. **Configuração Inicial**
1. Acesse `/admin-tools/`
2. Vá em **"Tipos de Turma"** → Crie os tipos necessários
3. Associe competências a cada tipo
4. Em **"Gerenciar Competências"** → Configure as avaliações

#### 2. **Importação de Alunos**
1. Clique em **"Importar Alunos"**
2. Faça upload de arquivo CSV/Excel com colunas:
   ```csv
   Nome Completo,Turma,Matricula
   João Silva,Basic 1 - MW18,2024001
   Maria Santos,HR4 - TT20,2024002
   ```
3. Selecione a turma de destino
4. Confirme a importação

#### 3. **Visualização de Analytics**
1. Acesse **"Gráficos Inteligentes"**
2. Analise os 4 gráficos disponíveis
3. Use tooltips para informações detalhadas

### Para Professores

#### 1. **Acesso ao Portal**
1. Acesse `/portal/`
2. Faça login com suas credenciais
3. Visualize suas turmas no dashboard

#### 2. **Lançamento de Notas**
1. Clique na turma desejada
2. Selecione o aluno
3. Escolha a competência
4. Insira a nota (numérica ou categórica)
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
- [ ] **Backup Automático**: Sincronização com cloud

### 🎯 Melhorias Planejadas
- [ ] **Testes Automatizados**: Cobertura >90%
- [ ] **Docker**: Containerização completa
- [ ] **CI/CD**: Pipeline de deploy automático
- [ ] **Monitoramento**: Logs e métricas avançadas
- [ ] **Multi-idiomas**: Internacionalização (i18n)

## 🐛 Suporte

### Problemas Comuns

#### Erro de Migração
```bash
# Resetar migrações (CUIDADO: perde dados!)
rm db.sqlite3
rm -rf core/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

#### Dependências
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
**Email**: [seu-email@exemplo.com](mailto:seu-email@exemplo.com)  
**GitHub**: [@RomuloCifer](https://github.com/RomuloCifer)  
**LinkedIn**: [Seu LinkedIn](https://linkedin.com/in/seu-perfil)

---

<div align="center">

**⭐ Se este projeto foi útil, deixe uma estrela! ⭐**

![Footer](docs/footer-banner.png)

*Desenvolvido com ❤️ para educadores e estudantes*

</div>