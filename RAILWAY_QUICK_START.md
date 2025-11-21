# 🚂 DEPLOY RAILWAY - COMANDOS RÁPIDOS

## ⚡ INÍCIO RÁPIDO

### 1️⃣ **Preparar Repositório GitHub**

```powershell
# Se ainda não tem Git inicializado
git init
git add .
git commit -m "Preparado para deploy no Railway"

# Criar repositório no GitHub e conectar
# Visite: https://github.com/new
# Nome sugerido: sistema-notas-escola
# MANTENHA PRIVADO!

git remote add origin https://github.com/SEU_USUARIO/sistema-notas-escola.git
git branch -M main
git push -u origin main
```

---

### 2️⃣ **Configurar Railway**

1. **Criar conta:** https://railway.app/ → Login com GitHub
2. **Novo Projeto:** "New Project" → "Deploy from GitHub repo"
3. **Selecionar repositório:** `sistema-notas-escola`

---

### 3️⃣ **Adicionar PostgreSQL**

1. No dashboard → **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Copiar **DATABASE_URL** da aba "Variables" do banco

---

### 4️⃣ **Configurar Variáveis de Ambiente**

No projeto (não no banco) → aba **"Variables"** → adicionar:

```env
DEBUG=False
SECRET_KEY=GERAR_AQUI
ALLOWED_HOSTS=.railway.app
CSRF_TRUSTED_ORIGINS=https://*.railway.app

DB_ENGINE=django.db.backends.postgresql
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=copiar_do_DATABASE_URL
DB_HOST=copiar_do_DATABASE_URL
DB_PORT=5432

USE_HTTPS=True
WHATSAPP_SUPPORT_NUMBER=5522999136252
```

**Gerar SECRET_KEY:**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**Extrair dados do DATABASE_URL:**
```
postgresql://usuario:senha@host:porta/banco
         ↓
DB_USER=usuario
DB_PASSWORD=senha
DB_HOST=host
DB_PORT=porta
DB_NAME=banco
```

---

### 5️⃣ **Rodar Migrações (Via Railway CLI)**

```powershell
# Instalar CLI
npm i -g @railway/cli

# Login
railway login

# Conectar ao projeto
railway link

# Rodar comandos
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
railway run python manage.py createsuperuser
```

**OU use o terminal web no dashboard do Railway.**

---

### 6️⃣ **Acessar o Site**

No Railway → **Settings** → copiar URL

```
https://seu-projeto.up.railway.app/admin-panel/  ← Admin
https://seu-projeto.up.railway.app/portal/       ← Professores
```

---

## 🔄 FAZER UPDATES

Sempre que editar o código:

```powershell
git add .
git commit -m "Descrição da mudança"
git push
```

Railway faz deploy automático! 🚀

---

## 🆘 PROBLEMAS COMUNS

### Site não abre
```powershell
# Ver logs no Railway
railway logs

# Verificar se variáveis estão corretas
railway variables
```

### CSS não carrega
```powershell
railway run python manage.py collectstatic --noinput
```

### Erro de banco de dados
- Verifique se `DB_HOST`, `DB_USER`, `DB_PASSWORD` estão corretos
- Copie novamente do `DATABASE_URL`

---

## 📋 CHECKLIST DEPLOY

- [ ] Código no GitHub (repositório privado)
- [ ] Projeto criado no Railway
- [ ] PostgreSQL adicionado
- [ ] Variáveis de ambiente configuradas
- [ ] SECRET_KEY gerada e adicionada
- [ ] Migrações rodadas (`migrate`)
- [ ] Arquivos estáticos coletados (`collectstatic`)
- [ ] Superusuário criado (`createsuperuser`)
- [ ] Admin funciona (`/admin-panel/`)
- [ ] Portal funciona (`/portal/`)

---

## 📞 CONTATO

**Dúvidas?** Me chame no chat! 💬

**Criado:** 21/11/2025
