🤖 Bot de Gerenciamento de Facções para Discord

Um bot completo para gerenciar facções em servidores Discord, com sistema de verificação automática de líderes, painel de controle e banco de dados integrado.
✨ Funcionalidades Principais
📊 Painel de Controle Interativo

    Visualização em tempo real do status das facções

    Contagem automática por status (Entregues, Recolhidas, Desativadas)

    Sistema de paginação para listas extensas

    Atualização automática do painel

🔍 Sistema de Verificação de Líderes

    Verificação automática a cada 10 minutos

    Monitoramento de 50+ cargos de líder pré-configurados

    Alertas automáticos para facções sem líderes

    Informações detalhadas sobre líderes atuais (nome, ID, quantidade)

📋 Gerenciamento Completo de Facções

    Novas facções: Registro com seleção de segmento

    Reentregas: Sistema simplificado que mantém segmento original

    Recolhimento: Registro com motivo e staff responsável

    Desativação: Controle total com histórico de motivos

🗃️ Banco de Dados SQLite

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

pip install discord.py sqlite3 datetime

    Configure o bot no Discord Developer Portal

        Crie uma nova aplicação em Discord Developer Portal

        Vá para a seção "Bot" e crie um bot

        Copie o token

        Ative os Privileged Gateway Intents:

            SERVER MEMBERS INTENT

            MESSAGE CONTENT INTENT

    Configure os canais
    No código principal, substitua os IDs dos canais:

python

CANAL_DESATIVADAS = 123456789012345678
CANAL_ENTREGUES   = 123456789012345678
CANAL_RECOLHIDAS  = 123456789012345678
CANAL_PAINEL      = 123456789012345678
CANAL_NOTIFICACAO = 123456789012345678

    Configure os cargos de líder
    Adicione ou modifique os IDs no dicionário CARGO_LIDERES:

python

CARGO_LIDERES = {
    1234567890123456789: "🦁・LÍDER ALEMANHA",
    9876543210987654321: "🏄・LÍDER BRONKS",
    # ... outros cargos
}

    Execute o bot

bash

python bot_faccoes.py

🎮 Comandos do Bot
Comandos no Discord

    .verificar_lideres - Verificação manual de facções sem líderes (apenas administradores)

    .lideres [nome_fac] - Mostra informações dos líderes de uma ou todas as facções

Painel de Controle (Interface Visual)

O bot cria um painel com os seguintes botões:
Botão	Funcionalidade	Descrição
📤 ENTREGAR FAC	Registrar nova facção ou reentrega	Sistema diferenciado para novas facções vs reentregas
📥 RECOLHER FAC	Recolher facção entregue	Registra motivo e staff responsável
⛔ DESATIVAR FAC	Desativar facção	Para facções entregues ou recolhidas
📊 STATUS FACÇÕES	Ver detalhes de uma facção	Mostra líderes atuais e histórico
🔄 ATUALIZAR PAINEL	Atualizar painel	Atualiza estatísticas em tempo real
📋 MOSTRAR FAC LIVRE	Facções disponíveis	Lista facções recolhidas para reentrega
🔍 VERIFICAR LÍDERES	Verificação manual	Checa facções sem líderes
🏗️ Estrutura do Banco de Dados

A tabela faccoes contém os seguintes campos:
Campo	Tipo	Descrição
nome	TEXT	Nome da facção (chave primária)
segmento	TEXT	Segmento (Armas, Munição, Lavagem, Drogas)
cds	TEXT	CDS da facção
termos	TEXT	Termos específicos
staff	TEXT	Staff responsável
lideres	TEXT	Líderes registrados
status	TEXT	Status atual (🟢 ENTREGUE, 🟡 RECOLHIDA, 🔴 DESATIVADA)
data	TEXT	Data de entrega
data_recolhida	TEXT	Data de recolhimento
data_desativada	TEXT	Data de desativação
motivo_recolhida	TEXT	Motivo do recolhimento
motivo_desativada	TEXT	Motivo da desativação
id_cargo_lider	TEXT	ID do cargo de líder correspondente
ultima_verificacao	TEXT	Data da última verificação de líderes
qtd_lideres	INTEGER	Quantidade de líderes ativos
nomes_lideres	TEXT	Nomes e IDs dos líderes atuais
🔧 Configuração Avançada
Personalização dos Segmentos

Para modificar os segmentos disponíveis, edite a classe SelectSegmento:
python

options=[
    discord.SelectOption(label="🔫 Armas"),
    discord.SelectOption(label="💣 Munição"),
    discord.SelectOption(label="🧪 Lavagem"),
    discord.SelectOption(label="💊 Drogas")
    # Adicione novos segmentos aqui
]

Intervalo de Verificação

Para alterar a frequência da verificação automática:
python

@tasks.loop(minutes=10)  # Altere para minutos, horas, etc.
async def verificar_lideres_periodicamente():

Adicionar Novos Cargos de Líder

Adicione novos IDs ao dicionário CARGO_LIDERES:
python

CARGO_LIDERES = {
    # ... cargos existentes
    999999999999999999: "🌟・LÍDER NOVA FACÇÃO",
}

🛡️ Segurança
Permissões Recomendadas

O bot necessita das seguintes permissões:

    View Channels - Para ver os canais

    Send Messages - Para enviar mensagens

    Embed Links - Para enviar embeds

    Read Message History - Para ler histórico

    Manage Messages - Para gerenciar mensagens (opcional)

    Add Reactions - Para adicionar reações

Backup do Banco de Dados

O banco de dados é salvo automaticamente no arquivo faccoes.db. Faça backups regulares deste arquivo.
📝 Fluxos de Trabalho
1. Registrar Nova Facção
text

📤 ENTREGAR FAC → 🆕 NOVA FACÇÃO → Seleciona segmento → Preenche dados → ✅ Facção registrada

2. Reentregar Facção Existente
text

📤 ENTREGAR FAC → 📦 ENTREGAR FAC EXISTENTE/LIVRE → Seleciona facção → ✅ Reentrega com segmento mantido

3. Recolher Facção
text

📥 RECOLHER FAC → Seleciona facção → Preenche motivo → ✅ Facção recolhida

4. Verificar Status
text

📊 STATUS FACÇÕES → Seleciona facção → 📊 Visualiza detalhes + líderes atuais

🚨 Solução de Problemas
Problemas Comuns

    Bot não responde

        Verifique se o token está correto

        Confirme as permissões do bot

        Verifique se os Intents estão ativados

    Erro de permissões

        Confira se o bot tem acesso aos canais

        Verifique os IDs dos canais no código

    Banco de dados não funciona

        Confirme se o arquivo faccoes.db tem permissões de escrita

        Verifique se a estrutura da tabela está correta

Logs e Depuração

O bot exibe logs no terminal com emojis indicativos:

    ✅ Operações bem-sucedidas

    ❌ Erros detectados

    ⚠️ Avisos importantes

    🔍 Verificações em andamento

🤝 Contribuição

    Fork o projeto

    Crie uma branch para sua feature (git checkout -b feature/AmazingFeature)

    Commit suas mudanças (git commit -m 'Add some AmazingFeature')

    Push para a branch (git push origin feature/AmazingFeature)

    Abra um Pull Request

📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
✨ Recursos Adicionais

    Sistema de notificações - Alertas automáticos no canal configurado

    Exportação de dados - Futura implementação para exportar relatórios

    API REST - Possibilidade de integração com outros sistemas

    Dashboard web - Interface web para visualização de dados

📞 Suporte

Para suporte, abra uma issue no repositório ou entre em contato pelos canais oficiais.
