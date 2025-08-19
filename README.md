# Nytheris Core - Encurtador de Links 🚀

<p align="center">
  <img alt="Status da CI" src="https://github.com/codennomad/nytheris_core/actions/workflows/ci.yml/badge.svg">
  <img alt="Python Version" src="https://img.shields.io/badge/python-3.11-blue.svg">
  <img alt="Framework" src="https://img.shields.io/badge/Framework-FastAPI-green.svg">
  <img alt="License" src="https://img.shields.io/badge/Licen%C3%A7a-MIT-blue.svg">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-24.0-blue?logo=docker">
</p>

Nytheris Core é um sistema robusto e completo para encurtamento de URLs, construído com uma arquitetura moderna de microsserviços. O projeto inclui um backend poderoso, workers assíncronos, bots de notificação, testes automatizados e um pipeline de Integração Contínua.

![Nytheris](./docs/nytheris.png)

 > "As paredes têm ouvidos… mas eu falo baixo o suficiente para que só quem deve ouvir, ouça." — Nytheris

---

## ✨ Funcionalidades

- **✅ Encurtamento Padrão:** Crie links curtos com códigos aleatórios e únicos.
- **✅ Apelidos Customizados:** Defina seus próprios apelidos para os links (ex: `/r/meu-evento`).
- **✅ Proteção por Senha:** Adicione uma senha para proteger o acesso a links sensíveis.
- **✅ Autodestruição por Cliques:** Configure um link para expirar após um número definido de acessos.
- **✅ Notificações em Tempo Real:** Receba alertas no Telegram e Discord para eventos importantes (criação de links, expiração, etc.).
- **✅ Bot Interativo:** Consulte estatísticas de cliques de qualquer link diretamente pelo Discord com o comando `/stats`.
- **✅ Frontend Simples:** Uma interface de usuário limpa para criar e visualizar os links encurtados.

---

## 🏛️ Arquitetura do Sistema

O sistema foi projetado com uma arquitetura de microsserviços para garantir alta performance e escalabilidade. As operações de escrita (como a contagem de cliques) são desacopladas da resposta ao usuário através de um sistema de mensageria (RabbitMQ), garantindo que os redirecionamentos sejam instantâneos.

- **API Principal (FastAPI):** Responsável por gerenciar a criação e as regras dos links.
- **Worker de Analytics (Python/Pika):** Processa os eventos de clique em segundo plano.
- **Bots Consumidores (Python/Pika):** Serviços independentes que ouvem a fila de alertas para notificar as plataformas de chat.
- **Banco de Dados (PostgreSQL):** Armazena de forma persistente todos os dados dos links.
- **Cache (Redis):** Utilizado para acelerar futuras otimizações de consulta.

---

## 💻 Stack de Tecnologias

| Categoria          | Tecnologia                                 |
| :----------------- | :----------------------------------------- |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy           |
| **Banco de Dados** | PostgreSQL, Redis, Alembic (migrações)     |
| **Mensageria** | RabbitMQ com Pika                          |
| **Observabilidade**| Loguru, Bots para Telegram e Discord       |
| **Testes** | Pytest, Pytest-Cov                         |
| **DevOps** | Docker, Docker Compose, GitHub Actions (CI)|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla), Nginx   |

---

## 🚀 Configuração e Execução

### Pré-requisitos
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/)

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git](https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git)
    cd SEU_REPOSITORIO
    ```

2.  **Configure as variáveis de ambiente:**
    Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env` e preencha com suas chaves e tokens.
    ```bash
    cp .env.example .env
    ```
    Agora, edite o arquivo `.env` com suas credenciais.

3.  **Construa e inicie os serviços:**
    Este comando irá construir as imagens Docker e iniciar todos os contêineres em segundo plano.
    ```bash
    docker compose up --build -d
    ```

4.  **Execute as migrações do banco de dados:**
    Com os serviços rodando, aplique as migrações para criar as tabelas no banco de dados.
    ```bash
    docker compose exec api alembic upgrade head
    ```

O sistema agora está totalmente no ar!

---

## 🌐 Como Usar

- **Frontend:** Acesse a interface do usuário no seu navegador:
  - `http://localhost:8080`

- **Documentação da API:** A documentação interativa (Swagger UI) está disponível em:
  - `http://localhost:8000/docs`

- **Painel do RabbitMQ:** Monitore as filas e mensagens em:
  - `http://localhost:15672` (Login: `guest` / `guest`)

---

## 🧪 Rodando os Testes

Para garantir que tudo está funcionando como esperado, você pode rodar a suíte de testes automatizados.

```bash
docker compose exec api pytest
```

Para ver um relatório de cobertura de testes:
```bash
docker compose exec api pytest --cov=Backend
```

## 🔄 Pipeline de CI

Este projeto usa GitHub Actions para Integração Contínua. A cada push ou pull request para as branches principais, o pipeline irá automaticamente:

     - Verificar a qualidade do código com flake8.

     - Construir todo o ambiente Docker.

     - Executar a suíte de testes completa com pytest.

Isso garante que a integridade e a qualidade do código sejam mantidas.

## 📄 Licença

Distribuído sob a Licença MIT. Veja o arquivo LICENSE para mais informações.

---

## 🙋‍♂️ Author
Gabriel Henrique

🔗 [LinkedIn](https://www.linkedin.com/in/gabrielhenrique-tech/)

📧 gabrielheh03@gmail.com
