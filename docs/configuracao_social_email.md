# Guia de Configuração: Login Social e Email 📧🔑

**Autor:** Zhang Wei (Arquitetura Backend)
**Objetivo:** Configurar credenciais para Google/GitHub e sistema de envio de emails.

---

## 1. Login Social (OAuth2)

Para que o login social funcione, precisamos registrar o "PyNerd" no Google e no GitHub para obter o `CLIENT_ID` e o `CLIENT_SECRET`.

### 🌍 A. Google OAuth2

1.  Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2.  Crie um **Novo Projeto** (ex: `PyNerd-Dev`).
3.  No menu lateral, vá em **APIs e Serviços** > **Tela de permissão OAuth**.
    - Selecione **Externo**.
    - Preencha o nome do App ("PyNerd"), email de suporte e dados de contato.
    - Salver e Continuar.
4.  Vá em **Credenciais** > **Criar Credenciais** > **ID do cliente OAuth**.
    - **Tipo de Aplicativo:** Aplicação da Web.
    - **Nome:** PyNerd Backend.
    - **Origens JavaScript autorizadas:** `http://localhost:8000` (e `http://localhost:3000` do frontend).
    - **URIs de redirecionamento autorizados:**
      - `http://localhost:8000/api/auth/complete/google-oauth2/`
5.  Copie o **ID do cliente** e a **Chave secreta** e coloque no seu arquivo `.env`:

```env
GOOGLE_CLIENT_ID=seu_id_gigante.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=sua_senha_secreta_do_google
```

### 🐙 B. GitHub OAuth2

1.  Acesse [GitHub Developer Settings](https://github.com/settings/developers).
2.  Clique em **New OAuth App**.
3.  Preencha:
    - **Application Name:** PyNerd.
    - **Homepage URL:** `http://localhost:8000`.
    - **Authorization callback URL:** `http://localhost:8000/api/auth/complete/github/`.
4.  Clique em **Register application**.
5.  Gere um **Client Secret**.
6.  Copie os dados para o `.env`:

```env
GITHUB_CLIENT_ID=seu_id_do_github
GITHUB_CLIENT_SECRET=sua_senha_secreta_do_github
```

---

## 2. Configuração de Email (SMTP)

O Django precisa saber como enviar os emails de ativação.

### 💻 Ambiente de Desenvolvimento (Console)

Atualmente configurado no `settings.py`. Os emails não são enviados de verdade, eles aparecem no terminal onde o server está rodando. Ótimo para testes.

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### 🚀 Ambiente de Produção (Gmail / SendGrid)

Para enviar de verdade, usaremos SMTP. Recomendo usar uma "Senha de App" do Gmail ou um serviço como Resend/SendGrid.

**Opção Grátis (Gmail com App Password):**

1.  Vá na [Conta Google > Segurança](https://myaccount.google.com/security).
2.  Ative a **Verificação em duas etapas**.
3.  Busque por **Senhas de app**.
4.  Crie uma nova (ex: "PyNerd Django").
5.  Copie a senha gerada (sem espaços).

Adicione no `.env`:

```env
# Mude para SMTPBackend em produção
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu.email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app_gerada
```

---

## ✅ Resumo do `.env` Final

Seu arquivo `.env` deve ficar assim:

```env
DEBUG=True
SECRET_KEY=sua_chave_secreta_django
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# Social Auth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# Email (Exemplo Gmail)
EMAIL_HOST_USER=seu.email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app
```
