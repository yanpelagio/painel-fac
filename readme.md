🤖 Bot de Gerenciamento de Facções para Discord
📋 Índice

    Visão Geral

    Funcionalidades

    Instalação

    Configuração

    Comandos

    Estrutura

    Fluxos

    Solução de Problemas

Visão Geral

Um bot completo para gerenciar facções em servidores Discord, com sistema de verificação automática de líderes, painel de controle e banco de dados SQLite integrado.
✨ Funcionalidades
✅ Painel de Controle Interativo

    Visualização em tempo real do status das facções

    Contagem automática por status (Entregues, Recolhidas, Desativadas)

    Sistema de paginação para listas extensas

    Atualização automática do painel

✅ Sistema de Verificação de Líderes

    Verificação automática a cada 10 minutos

    Monitoramento de 50+ cargos de líder pré-configurados

    Alertas automáticos para facções sem líderes

    Informações detalhadas sobre líderes atuais

✅ Gerenciamento Completo de Facções

    Novas facções: Registro com seleção de segmento

    Reentregas: Sistema simplificado (mantém segmento original)

    Recolhimento: Registro com motivo e staff responsável

    Desativação: Controle total com histórico de motivos

✅ Banco de Dados SQLite

    Armazenamento persistente de todas as informações

    Histórico completo de alterações

    Backup automático de dados

🚀 Instalação
Pré-requisitos

    Python 3.8 ou superior

    Discord Developer Account

    Servidor Discord com permissões administrativas

Passo a Passo

    Clone o repositório

bash

git clone https://github.com/seu-usuario/bot-faccoes.git
cd bot-faccoes

    Instale as dependências

bash

pip install discord.py

    Configure o bot no Discord Developer Portal

        Acesse: https://discord.com/developers/applications

        Crie uma nova aplicação

        Vá para "Bot" → "Add Bot"

        Copie o token

        Ative os Intents:

            ✅ SERVER MEMBERS INTENT

            ✅ MESSAGE CONTENT INTENT

    Execute o bot

bash

python bot_faccoes.py

⚙️ Configuração
Configuração dos Canais

No código principal, substitua os IDs dos canais:
python

# IDs dos canais
CANAL_DESATIVADAS = 123456789012345678
CANAL_ENTREGUES   = 123456789012345678
CANAL_RECOLHIDAS  = 123456789012345678
CANAL_PAINEL      = 123456789012345678
CANAL_NOTIFICACAO = 123456789012345678

Configuração dos Cargos de Líder

Adicione/modifique os IDs no dicionário CARGO_LIDERES:
python

CARGO_LIDERES = {
    1348039634596397199: "🦁・LÍDER ALEMANHA",
    1441606357500563709: "🏄・LÍDER BRONKS",
    # Adicione mais cargos aqui...
}

🎮 Comandos
Comandos de Texto
Comando	Permissão	Descrição
.verificar_lideres	Administrador	Verificação manual de facções sem líderes
.lideres [nome]	Todos	Mostra líderes de uma ou todas as facções
