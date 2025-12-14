Bot de Gerenciamento de Facções Discord


Um bot completo para gerenciar facções em servidores Discord com sistema de verificação automática de líderes, painel de controle e banco de dados SQLite.
📋 Índice

    Visão Geral

    Funcionalidades Principais

    Instalação

    Configuração

    Comandos

    Estrutura do Banco de Dados

    Fluxos de Trabalho

    Solução de Problemas

    Configuração Avançada

    Segurança

    Contribuição

    Licença

Visão Geral

Bot desenvolvido para comunidades Discord que precisam gerenciar facções de forma organizada. Inclui sistema automático de verificação de líderes a cada 10 minutos, painel interativo e histórico completo de todas as operações.
Funcionalidades Principais
Painel de Controle Interativo

    Visualização em tempo real do status das facções

    Contagem automática por status (Entregues, Recolhidas, Desativadas)

    Sistema de paginação para listas extensas

    Atualização automática

Sistema de Verificação de Líderes

    Verificação automática a cada 10 minutos

    Monitoramento de 50+ cargos de líder

    Alertas automáticos para facções sem líderes

    Informações detalhadas sobre líderes atuais

Gerenciamento Completo

    Novas facções com seleção de segmento

    Reentregas simplificadas (mantém segmento original)

    Recolhimento com motivo e staff

    Desativação com histórico

Banco de Dados

    SQLite para armazenamento persistente

    Histórico completo de alterações

    Backup automático    

Instalação
Pré-requisitos

    Python 3.8 ou superior

    Discord Developer Account

    Servidor Discord com permissões

Passo a Passo

    Clone o repositório:

text

git clone https://github.com/seu-usuario/bot-faccoes.git
cd bot-faccoes

    Instale as dependências:

text

pip install discord.py python-dotenv

    Configure no Discord Developer Portal:

        Acesse https://discord.com/developers/applications

        Crie nova aplicação

        Vá em Bot → Add Bot

        Copie o token

        Ative SERVER MEMBERS INTENT

        Ative MESSAGE CONTENT INTENT

    Configure os IDs dos canais no código:

        CANAL_DESATIVADAS

        CANAL_ENTREGUES

        CANAL_RECOLHIDAS

        CANAL_PAINEL

        CANAL_NOTIFICACAO

    Configure os cargos de líder no dicionário CARGO_LIDERES

    Execute:

text

python bot_faccoes.py

Configuração
Configuração dos Canais

No início do arquivo bot_faccoes.py, configure os IDs:
text

CANAL_DESATIVADAS = 123456789012345678
CANAL_ENTREGUES   = 123456789012345678
CANAL_RECOLHIDAS  = 123456789012345678
CANAL_PAINEL      = 123456789012345678
CANAL_NOTIFICACAO = 123456789012345678

Configuração dos Cargos

Adicione IDs de cargo no dicionário CARGO_LIDERES:
text

CARGO_LIDERES = {
    1348039634596397199: "LÍDER ALEMANHA",
    1441606357500563709: "LÍDER BRONKS",
    # Adicione mais...
}

Variáveis de Ambiente

Para produção, use variáveis de ambiente:

    DISCORD_TOKEN: Token do bot Discord

    Configurado no SquareCloud ou arquivo .env

Comandos
Comandos de Texto

    .verificar_lideres - Verificação manual (apenas admin)

    .lideres [nome] - Mostra líderes de facções

Painel de Controle (Botões)

O bot cria um painel com botões interativos:

    ENTREGAR FAC - Registrar nova facção ou reentrega

    RECOLHER FAC - Recolher facção entregue

    DESATIVAR FAC - Desativar facção

    STATUS FACÇÕES - Ver detalhes de uma facção

    ATUALIZAR PAINEL - Atualizar estatísticas

    MOSTRAR FAC LIVRE - Facções disponíveis para reentrega

    VERIFICAR LÍDERES - Verificação manual

Estrutura do Banco de Dados
Tabela: faccoes

Campos armazenados:

    nome: Nome da facção

    segmento: Segmento (Armas, Munição, etc)

    cds: CDS da facção

    termos: Termos específicos

    staff: Staff responsável

    lideres: Líderes registrados

    status: Status atual

    data: Data de entrega

    data_recolhida: Data de recolhimento

    data_desativada: Data de desativação

    motivo_recolhida: Motivo do recolhimento

    motivo_desativada: Motivo da desativação

    id_cargo_lider: ID do cargo de líder

    ultima_verificacao: Última verificação

    qtd_lideres: Quantidade de líderes ativos

    nomes_lideres: Nomes dos líderes atuais

Fluxos de Trabalho
1. Nova Facção

    Clique em ENTREGAR FAC

    Selecione NOVA FACÇÃO

    Escolha segmento

    Preencha dados

    Facção registrada

2. Reentregar Facção

    Clique em ENTREGAR FAC

    Selecione ENTREGAR FAC EXISTENTE

    Escolha facção

    Reentrega com segmento mantido

3. Recolher Facção

    Clique em RECOLHER FAC

    Selecione facção

    Preencha motivo

    Facção recolhida

4. Verificar Status

    Clique em STATUS FACÇÕES

    Selecione facção

    Veja detalhes + líderes

Solução de Problemas
Problemas Comuns

    Bot não responde

        Verifique token

        Confirme permissões

        Verifique Intents

    Erro de permissões

        Confirme IDs dos canais

        Verifique acesso do bot

    Banco de dados não funciona

        Verifique permissões de escrita

        Confirme estrutura da tabela

    Erro "TypeError"

        Execute novamente

        Verifique conversão de tipos

Logs do Sistema

    Operações bem-sucedidas

    Erros detectados

    Avisos importantes

    Verificações em andamento

Configuração Avançada
Alterar Segmentos

Edite em SelectSegmento:
text

options=[
    discord.SelectOption(label="Armas"),
    discord.SelectOption(label="Munição"),
    discord.SelectOption(label="Lavagem"),
    discord.SelectOption(label="Drogas")
]

Alterar Frequência

Mude o valor em minutes:
text

@tasks.loop(minutes=10)  # Altere este valor
async def verificar_lideres_periodicamente():

Segurança
Permissões Necessárias

    View Channels

    Send Messages

    Embed Links

    Read Message History

    Manage Messages (opcional)

    Add Reactions

Backup

    Banco salvo em faccoes.db

    Faça backups regulares

    Não compartilhe tokens

Para SquareCloud
Configuração

Crie arquivo squarecloud.app:
text

{
  "displayName": "Bot Facções",
  "main": "bot_faccoes.py",
  "memory": 100,
  "description": "Bot para gerenciamento de facções",
  "version": "2.0.0",
  "language": "python",
  "start": "python bot_faccoes.py"
}

Variáveis no SquareCloud

    DISCORD_TOKEN: Seu token do bot

Contribuição

    Faça Fork

    Crie Branch (git checkout -b feature/nova)

    Commit (git commit -m 'Add nova')

    Push (git push origin feature/nova)

    Abra Pull Request

Licença

MIT License - veja LICENSE para detalhes.
Suporte

    Issues: GitHub Issues

    Discord: Servidor oficial

Versão

2.0.0 - Dezembro 2023
Python 3.8+
Discord.py 2.0+
Recursos Futuros

    Exportação de relatórios

    API REST

    Dashboard web

    Sistema de logs avançado

    Multi-servidor

Desenvolvido para comunidades Discord
