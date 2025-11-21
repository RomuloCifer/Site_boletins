# ✅ CHECKLIST DE DEPLOY - RAILWAY

Use este checklist para garantir que tudo está configurado corretamente!

---

## 📝 ANTES DO DEPLOY

### Código Preparado
- [ ] Arquivo `Procfile` criado ✅ (já feito)
- [ ] Arquivo `runtime.txt` criado ✅ (já feito)
- [ ] Arquivo `railway.json` criado ✅ (já feito)
- [ ] Arquivo `.gitignore` protege `.env` e `db.sqlite3` ✅ (já feito)
- [ ] Arquivo `requirements.txt` atualizado ✅ (já feito)

---

## 🐙 GITHUB

- [ ] Conta GitHub criada
- [ ] Repositório criado (nome: `sistema-notas-escola`)
- [ ] Repositório é **PRIVADO** (protege seus dados!)
- [ ] Código enviado para GitHub (`git push`)

**Comandos:**
```powershell
git init
git add .
git commit -m "Deploy preparado para Railway"
git remote add origin https://github.com/SEU_USUARIO/sistema-notas-escola.git
git branch -M main
git push -u origin main
```

---

## 🚂 RAILWAY - CONFIGURAÇÃO INICIAL

### Conta e Projeto
- [ ] Conta Railway criada (https://railway.app/)
- [ ] Login feito com GitHub
- [ ] Projeto criado: "Deploy from GitHub repo"
- [ ] Repositório `sistema-notas-escola` selecionado

### Banco de Dados PostgreSQL
- [ ] PostgreSQL adicionado: "+ New" → "Database" → "PostgreSQL"
- [ ] `DATABASE_URL` copiado da aba "Variables" do banco
- [ ] Dados extraídos do `DATABASE_URL`:
  ```
  postgresql://usuario:senha@host:porta/banco
  
  DB_USER = usuario
  DB_PASSWORD = senha
  DB_HOST = host
  DB_PORT = porta (geralmente 5432)
  DB_NAME = banco (geralmente railway)
  ```

---

## 🔐 VARIÁVEIS DE AMBIENTE

No projeto Railway → aba "Variables" → adicionar:

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY=` (gerada com `python gerar_secret_key.py`)
- [ ] `ALLOWED_HOSTS=.railway.app`
- [ ] `CSRF_TRUSTED_ORIGINS=https://*.railway.app`
- [ ] `DB_ENGINE=django.db.backends.postgresql`
- [ ] `DB_NAME=railway` (ou valor do DATABASE_URL)
- [ ] `DB_USER=` (extraído do DATABASE_URL)
- [ ] `DB_PASSWORD=` (extraído do DATABASE_URL)
- [ ] `DB_HOST=` (extraído do DATABASE_URL)
- [ ] `DB_PORT=5432`
- [ ] `USE_HTTPS=True`
- [ ] `WHATSAPP_SUPPORT_NUMBER=5522999136252` (opcional)

---

## 🚀 DEPLOY INICIAL

- [ ] Railway fez deploy automático (aguardar 2-5 minutos)
- [ ] Logs não mostram erros críticos
- [ ] URL do site disponível (Settings → Domain)

---

## 💾 CONFIGURAR BANCO DE DADOS

### Via Railway CLI (Recomendado)
```powershell
npm i -g @railway/cli
railway login
railway link
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
railway run python manage.py createsuperuser
```

### Ou via Terminal Web
- [ ] Acessar terminal no dashboard do Railway
- [ ] Rodar: `python manage.py migrate`
- [ ] Rodar: `python manage.py collectstatic --noinput`
- [ ] Rodar: `python manage.py createsuperuser`

---

## 🧪 TESTES FINAIS

### Portal Admin
- [ ] Abrir: `https://seu-site.railway.app/admin-panel/`
- [ ] Login com superusuário funciona
- [ ] Interface carrega corretamente (com CSS)
- [ ] Consegue ver modelos: Professores, Alunos, Turmas, etc.

### Portal do Professor
- [ ] Criar um professor de teste no admin
- [ ] Abrir: `https://seu-site.railway.app/portal/`
- [ ] Login do professor funciona
- [ ] Dashboard carrega

### Persistência de Dados
- [ ] Criar um aluno de teste no admin
- [ ] Fechar navegador completamente
- [ ] Abrir novamente e fazer login
- [ ] Aluno ainda está lá ✅ (PostgreSQL funcionando!)

### HTTPS e Segurança
- [ ] URL começa com `https://` (cadeado no navegador)
- [ ] Não há avisos de segurança
- [ ] CSS e JavaScript carregam corretamente

---

## 📱 PREPARAR PARA PROFESSORES

- [ ] Criar grupos de permissões (se necessário)
- [ ] Adicionar professores iniciais no admin
- [ ] Criar turmas e associar professores
- [ ] Testar lançamento de notas
- [ ] Testar geração de PDFs/boletins

---

## 📊 MONITORAMENTO

### No Railway
- [ ] Verificar uso de recursos (Dashboard → Metrics)
- [ ] Configurar alertas (opcional)
- [ ] Verificar logs regularmente

---

## 🔄 WORKFLOW DE ATUALIZAÇÕES

Quando fizer mudanças no código:

```powershell
# 1. Fazer mudanças localmente
# 2. Testar localmente
# 3. Enviar para GitHub
git add .
git commit -m "Descrição clara da mudança"
git push

# 4. Railway faz deploy automático!
# 5. Verificar logs no Railway
```

- [ ] Processo de atualização testado e funcionando

---

## 💰 CUSTOS E LIMITES

- [ ] Verificado créditos disponíveis ($5 grátis)
- [ ] Entendido que após créditos: ~$5-10/mês
- [ ] Configurado método de pagamento (se necessário)

---

## 📞 SUPORTE

### Problemas Comuns

**Site não abre (502/503)**
- Verificar logs: `railway logs`
- Verificar se todas variáveis estão corretas
- Verificar se migrations rodaram

**CSS não carrega**
- Rodar: `railway run python manage.py collectstatic --noinput`
- Verificar se `STATIC_ROOT` está configurado

**Erro de banco de dados**
- Verificar credenciais do PostgreSQL
- Verificar se `DB_HOST`, `DB_USER`, `DB_PASSWORD` estão corretos
- Re-copiar do `DATABASE_URL`

**"DisallowedHost" error**
- Adicionar domínio em `ALLOWED_HOSTS`
- Adicionar em `CSRF_TRUSTED_ORIGINS`

---

## ✅ DEPLOY CONCLUÍDO COM SUCESSO

Quando todos os itens acima estiverem marcados:

🎉 **PARABÉNS!** Seu sistema está online e funcionando!

**Próximos passos:**
1. Adicionar professores e alunos
2. Configurar turmas
3. Treinar professores para usar o sistema
4. Monitorar uso e performance

---

## 📝 ANOTAÇÕES PESSOAIS

**URL do site:**
```
https://_____________________________________.up.railway.app
```

**Superusuário criado:**
```
Username: ___________________
Email: ______________________
Senha: (guardada em lugar seguro)
```

**Data do deploy:**
```
___/___/2025
```

**Problemas encontrados e soluções:**
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

**Criado em:** 21/11/2025  
**Sistema:** Sistema de Notas v1.0  
**Plataforma:** Railway.app
