# 🎬 COMEÇAR AGORA - PASSO A PASSO VISUAL

Siga exatamente nesta ordem para colocar seu sistema online em ~30 minutos!

---

## ✅ PASSO 1: VALIDAR PROJETO (2 min)

Abra o terminal no VS Code e rode:

```powershell
python verificar_pre_deploy.py
```

**Resultado esperado:** Todos ✅ verdes, nenhum ❌ vermelho

---

## ✅ PASSO 2: GERAR SECRET_KEY (1 min)

```powershell
python gerar_secret_key.py
```

**IMPORTANTE:** 
- 📋 Copie a chave gerada
- 💾 Cole em um bloco de notas temporário
- ⚠️ Você vai precisar dela no Passo 6!

---

## ✅ PASSO 3: SUBIR PARA GITHUB (5 min)

### 3.1 - Criar repositório no GitHub

1. Abra: https://github.com/new
2. Nome: `sistema-notas-escola`
3. **IMPORTANTE:** Marque como **PRIVADO** 🔒
4. Clique "Create repository"
5. **NÃO FECHE A PÁGINA** (você vai precisar da URL)

### 3.2 - Enviar código

No terminal do VS Code:

```powershell
# Se ainda não tem Git inicializado
git init

# Adicionar todos os arquivos
git add .

# Fazer commit inicial
git commit -m "Sistema pronto para deploy"

# Conectar com GitHub (SUBSTITUA seu-usuario!)
git remote add origin https://github.com/seu-usuario/sistema-notas-escola.git

# Enviar para GitHub
git branch -M main
git push -u origin main
```

**Resultado esperado:** Código aparece no GitHub! 🎉

---

## ✅ PASSO 4: CRIAR CONTA RAILWAY (3 min)

1. Abra: https://railway.app/
2. Clique em **"Start a New Project"** ou **"Login"**
3. Escolha **"Login with GitHub"**
4. Autorize o Railway a acessar sua conta
5. **Pronto!** Você está logado no Railway

---

## ✅ PASSO 5: CRIAR PROJETO NO RAILWAY (2 min)

1. No dashboard do Railway, clique **"New Project"**
2. Escolha **"Deploy from GitHub repo"**
3. Se pedir permissão, autorize o Railway a ver seus repositórios
4. Na lista, clique em **"sistema-notas-escola"**
5. Railway começa a fazer deploy (aguarde ~2 minutos)

**O que está acontecendo:**
- Railway está lendo seu código
- Instalando dependências do `requirements.txt`
- Tentando iniciar a aplicação

**AINDA VAI DAR ERRO** - normal! Falta o banco de dados. Continue!

---

## ✅ PASSO 6: ADICIONAR POSTGRESQL (2 min)

No dashboard do Railway:

1. Clique no botão **"+ New"** (canto superior direito)
2. Escolha **"Database"**
3. Clique em **"Add PostgreSQL"**
4. Railway cria o banco automaticamente! 🗄️

### 6.1 - Copiar credenciais do banco

1. Clique no **ícone do PostgreSQL** que apareceu
2. Vá na aba **"Variables"**
3. Encontre a variável **`DATABASE_URL`**
4. Clique para **copiar o valor completo**
5. Cole em um bloco de notas

**Exemplo do DATABASE_URL:**
```
postgresql://postgres:AbCdEfG123@containers-us-west-123.railway.app:5432/railway
```

### 6.2 - Extrair informações

Do exemplo acima, extraia:

```
DB_USER = postgres
DB_PASSWORD = AbCdEfG123
DB_HOST = containers-us-west-123.railway.app
DB_PORT = 5432
DB_NAME = railway
```

**IMPORTANTE:** Anote esses valores! Você vai usar no próximo passo.

---

## ✅ PASSO 7: CONFIGURAR VARIÁVEIS (7 min)

### 7.1 - Acessar configurações do projeto

1. No dashboard do Railway
2. Clique no **seu projeto** (NÃO no PostgreSQL)
3. Vá na aba **"Variables"**

### 7.2 - Adicionar variáveis UMA POR UMA

Clique em **"+ New Variable"** e adicione:

#### Variável 1: DEBUG
```
Name: DEBUG
Value: False
```

#### Variável 2: SECRET_KEY
```
Name: SECRET_KEY
Value: [COLE A CHAVE QUE VOCÊ GEROU NO PASSO 2]
```

#### Variável 3: ALLOWED_HOSTS
```
Name: ALLOWED_HOSTS
Value: .railway.app
```

#### Variável 4: CSRF_TRUSTED_ORIGINS
```
Name: CSRF_TRUSTED_ORIGINS
Value: https://*.railway.app
```

#### Variável 5: DB_ENGINE
```
Name: DB_ENGINE
Value: django.db.backends.postgresql
```

#### Variável 6: DB_NAME
```
Name: DB_NAME
Value: railway
```

#### Variável 7: DB_USER
```
Name: DB_USER
Value: [COLE O DB_USER QUE VOCÊ EXTRAIU NO PASSO 6.2]
```

#### Variável 8: DB_PASSWORD
```
Name: DB_PASSWORD
Value: [COLE O DB_PASSWORD QUE VOCÊ EXTRAIU NO PASSO 6.2]
```

#### Variável 9: DB_HOST
```
Name: DB_HOST
Value: [COLE O DB_HOST QUE VOCÊ EXTRAIU NO PASSO 6.2]
```

#### Variável 10: DB_PORT
```
Name: DB_PORT
Value: 5432
```

#### Variável 11: USE_HTTPS
```
Name: USE_HTTPS
Value: True
```

### 7.3 - Salvar e aguardar redeploy

Depois de adicionar todas as variáveis:
- Railway faz redeploy automaticamente
- Aguarde 2-3 minutos
- Veja os logs para verificar se não há erros

---

## ✅ PASSO 8: RODAR MIGRATIONS (5 min)

### 8.1 - Instalar Railway CLI

No terminal do VS Code (no seu PC):

```powershell
npm i -g @railway/cli
```

Se não tiver npm/node instalado:
- Baixe Node.js: https://nodejs.org/
- Instale e reinicie o terminal

### 8.2 - Fazer login

```powershell
railway login
```

Abre o navegador → clique em "Authorize"

### 8.3 - Conectar ao projeto

```powershell
railway link
```

Selecione seu projeto `sistema-notas-escola` na lista

### 8.4 - Rodar comandos

**Comando 1:** Criar tabelas no PostgreSQL
```powershell
railway run python manage.py migrate
```

**Comando 2:** Coletar arquivos estáticos (CSS, JS)
```powershell
railway run python manage.py collectstatic --noinput
```

**Comando 3:** Criar seu primeiro administrador
```powershell
railway run python manage.py createsuperuser
```

Preencha:
- **Username:** (seu nome de usuário)
- **Email:** (seu email)
- **Password:** (senha forte - digite 2x)

---

## ✅ PASSO 9: PEGAR URL DO SITE (1 min)

1. No dashboard do Railway
2. Clique no seu projeto
3. Vá na aba **"Settings"**
4. Na seção **"Domains"**, veja a URL
5. Exemplo: `https://sistema-notas-escola-production.up.railway.app`

**COPIE ESSA URL** - é o endereço do seu site! 🌐

---

## ✅ PASSO 10: TESTAR O SISTEMA (3 min)

### 10.1 - Testar Admin

1. Abra: `https://sua-url.railway.app/admin-panel/`
2. Faça login com o superusuário criado
3. **Deve funcionar!** ✅

Se aparecer a tela de login do admin com cores e tudo = **SUCESSO!** 🎉

### 10.2 - Criar professor de teste

No admin:
1. Vá em **"Professores"** → **"Adicionar professor"**
2. Preencha os dados
3. Salve

### 10.3 - Testar Portal do Professor

1. Abra: `https://sua-url.railway.app/portal/`
2. Faça login com o professor criado
3. **Deve funcionar!** ✅

---

## 🎉 PRONTO! SEU SISTEMA ESTÁ ONLINE!

### ✅ O que você conseguiu:

- ✅ Sistema online 24/7
- ✅ URL para compartilhar com professores
- ✅ Banco PostgreSQL salvando tudo
- ✅ HTTPS seguro (cadeado verde 🔒)
- ✅ Dados protegidos e permanentes

---

## 📱 COMPARTILHAR COM PROFESSORES

Envie esta mensagem:

```
🎓 Sistema de Notas - Portal do Professor

📍 Acesse: https://sua-url.railway.app/portal/

Faça login com:
👤 Username: [username_professor]
🔑 Senha: [senha_temporária]

⚠️ IMPORTANTE: Mude sua senha no primeiro acesso!

📞 Dúvidas? Me chame no WhatsApp: [seu número]
```

---

## 🔄 FAZER MUDANÇAS NO FUTURO

Sempre que editar o código localmente:

```powershell
git add .
git commit -m "Descrição do que mudou"
git push
```

**Railway faz deploy automático em ~2 minutos!** 🚀

---

## 🆘 PROBLEMAS?

### Site não abre (502 Error)
```powershell
railway logs
```
Veja o erro nos logs e me mande (posso ajudar!)

### CSS não aparece
```powershell
railway run python manage.py collectstatic --noinput
```

### Esqueci senha do admin
```powershell
railway run python manage.py changepassword seu_username
```

---

## 💡 DICAS FINAIS

1. **Anote suas credenciais** em lugar seguro
2. **Guarde a URL do site**
3. **Faça backup** da SECRET_KEY
4. **Não compartilhe** as variáveis de ambiente
5. **Monitore os custos** no Railway (primeiros $5 grátis)

---

## 📞 ME CHAME SE PRECISAR!

Qualquer erro, problema ou dúvida - **estou aqui para ajudar!** 💪

---

**Criado:** 21/11/2025  
**Tempo estimado:** 30 minutos  
**Dificuldade:** 🟢 Iniciante

---

## 🎯 AGORA É COM VOCÊ!

**COMECE PELO PASSO 1** e vá seguindo um por um!

Boa sorte! 🚀🎉
