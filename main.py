
# ==================== IMPORTS ====================
import os
import sys
import discord
from discord.ext import commands, tasks
import datetime
import sqlite3
import asyncio

# ==================== CONFIGURAÇÃO ====================
# Carregar token
TOKEN = os.getenv('DISCORD_TOKEN')

# Backup: tentar carregar de .env (para desenvolvimento local)
if not TOKEN:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        TOKEN = os.getenv('DISCORD_TOKEN')
    except ImportError:
        pass

# Verificação FINAL
if not TOKEN:
    print("❌ ERRO: Token não encontrado!")
    print("Configure DISCORD_TOKEN no SquareCloud ou crie um arquivo .env")
    sys.exit(1)

print(f"✅ Token carregado: {'*' * 20}{TOKEN[-10:] if TOKEN else 'NONE'}")

# Dicionário de IDs de cargo de líderes
CARGO_LIDERES = {
    1348039634596397199: "🦁・LÍDER ALEMANHA",
    1441606357500563709: "🏄・ LÍDER BRONKS",
    1161510495933714463: "✨・LÍDER CROÁCIA",
    1410826176439517204: "🔪・LÍDER DINASTIA",
    1347991203827814622: "🏺・ LÍDER EGITO",
    1082443562593030276: "🏛️・LÍDER GRÉCIA",
    1413703412301824040: "👑・LÍDER IMPÉRIO",
    1082445092742250628: "🛵・LÍDER INGLATERRA",
    885519379687698442: "🍕・LÍDER ITÁLIA",
    885519381881303060: "🤬・LÍDER METEBALA",
    1437286394031636601: "👺・LÍDER TROPA",
    1444439590290325515: "🍚・LÍDER NATTO",
    1444443292501545153: "🎱・LÍDER COMANDO",
    903453071986819103: "🃏・LÍDER ALCATEIA",
    885519384355938324: "🧩・LÍDER ABUTRES",
    988589194031038484: "🪽・LÍDER ARCANJO",
    1348041083246084270: "🔑・LÍDER BABEL",
    1348043503787180143: "💎・LIDER DIAMOND",
    1161510486815289415: "🐉・LÍDER DRAGONS",
    1412628666856374443: "🥢・LÍDER CHINA",
    885519401758109706: "🔥・LÍDER ELEMENTS",
    920197635086897162: "🦅・LÍDER FALCONS",
    1349861936610934814: "🔫・LIDER IRMANDADE",
    913528055157379092: "🥠・LÍDER KOREIA",
    1079861738910007377: "🐺・LÍDER WOLVES",
    1443004272265527347: "🌂・LÍDER UMBRELLA",
    1445551196411662346: "🌶・LIDER MEXICO",
    1444578804084244480: "💵・LÍDER MEDELLIN",
    1417296351141564436: "🧨・LIDER ABSOLUT",
    885519403981078598: "⚡・LÍDER AUSTRIA",
    1410842867819090041: "🍸・LIDER BAHAMAS",
    1185821767869136936: "⚽・LÍDER BRASIL",
    894618798236258406: "🍹・LÍDER COLOMBIA",
    1348044905947332660: "🪐・LÍDER GALAXY",
    1282343256692232236: "⛩️・LÍDER JAPÃO",
    1075468073018077244: "🪙・LÍDER PORTUGAL",
    1354294739939360788: "🔰・LÍDER B13",
    1437296001663766639: "✖️・LÍDER RENEGADOS",
    1140821129284571136: "🔵・LÍDER ARGENTINA",
    1438312774508875817: "😈・LÍDER FURIOUS",
    930101285150138391: "✈️・LÍDER BELGICA",
    885519375354978364: "🍁・LÍDER CANADÁ",
    1216263344533672037: "🤺・LÍDER ESPANHA",
    1161510522097774613: "🗼・LÍDER FRANÇA",
    1161510512140501132: "🟢・LÍDER GREENS",
    1082445393247346699: "🎯・LÍDER GROTTA",
    885519399249915974: "👻・LÍDER HOLANDA",
    885519396251004948: "🌿・LÍDER JAMAICA",
    885519394007040000: "🟣・LÍDER OS ROXOS",
    1282339411928944772: "💠・LÍDER CPX",
    918922790042734682: "🔱・LÍDER NORUEGA",
    1093404018472140800: "🕌・LÍDER TURQUIA",
    1438197297178742804: "👻・LÍDER GHOSTS"
}

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=".", intents=intents)

db = sqlite3.connect("faccoes.db")
cursor = db.cursor()

# ATUALIZAR A ESTRUTURA DA TABELA
cursor.execute("""
CREATE TABLE IF NOT EXISTS faccoes(
    nome TEXT PRIMARY KEY,
    segmento TEXT,
    cds TEXT,
    termos TEXT,
    staff TEXT,
    lideres TEXT,
    status TEXT,
    data TEXT,
    data_recolhida TEXT,
    data_desativada TEXT,
    motivo_recolhida TEXT,
    motivo_desativada TEXT,
    id_cargo_lider TEXT,
    ultima_verificacao TEXT,
    qtd_lideres INTEGER,
    nomes_lideres TEXT
)
""")
db.commit()

# VERIFICAR E ADICIONAR COLUNAS FALTANTES
def verificar_colunas():
    cursor.execute("PRAGMA table_info(faccoes)")
    colunas_existentes = [coluna[1] for coluna in cursor.fetchall()]
    colunas_necessarias = [
        "nome", "segmento", "cds", "termos", "staff", "lideres", "status", "data",
        "data_recolhida", "data_desativada", "motivo_recolhida", "motivo_desativada",
        "id_cargo_lider", "ultima_verificacao", "qtd_lideres", "nomes_lideres"
    ]
    
    for coluna in colunas_necessarias:
        if coluna not in colunas_existentes:
            cursor.execute(f"ALTER TABLE faccoes ADD COLUMN {coluna} TEXT")
            print(f"✅ Coluna {coluna} adicionada à tabela")
    
    db.commit()

verificar_colunas()

# Função para obter nome da facção pelo ID do cargo
def obter_fac_por_cargo(id_cargo):
    for cargo_id, fac_nome in CARGO_LIDERES.items():
        if cargo_id == id_cargo:
            nome = fac_nome.split("・")[-1].strip()
            return nome
    return None

# Função para obter nome do cargo pelo nome da facção
def obter_id_cargo_por_fac(nome_fac):
    for cargo_id, fac_nome in CARGO_LIDERES.items():
        if nome_fac.lower() in fac_nome.lower():
            return cargo_id
    return None

# Função para obter informações dos líderes atuais
async def obter_lideres_atuais(guild, id_cargo):
    """Retorna lista de líderes atuais para um cargo"""
    cargo = guild.get_role(id_cargo)
    if not cargo:
        return []
    
    membros_com_cargo = [membro for membro in guild.members if cargo in membro.roles]
    lideres_info = []
    
    for membro in membros_com_cargo:
        lideres_info.append({
            "nome": membro.name,
            "id": membro.id,
            "menção": membro.mention
        })
    
    return lideres_info

# Função principal para verificar líderes
async def verificar_lideres_no_servidor(guild):
    """Verifica se há membros com os cargos de líder"""
    cargos_sem_lideres = []
    
    for cargo_id, fac_nome in CARGO_LIDERES.items():
        nome_fac = obter_fac_por_cargo(cargo_id)
        
        if not nome_fac:
            continue
            
        fac_data = carregar_fac(nome_fac)
        if not fac_data:
            continue
            
        if fac_data["status"] != "🟢 ENTREGUE":
            continue
            
        cargo = guild.get_role(cargo_id)
        if not cargo:
            continue
            
        membros_com_cargo = [membro for membro in guild.members if cargo in membro.roles]
        
        # Atualizar informações dos líderes no banco de dados
        atualizar_informacoes_lideres(nome_fac, membros_com_cargo, guild)
        
        if not membros_com_cargo:
            cargos_sem_lideres.append({
                "id_cargo": cargo_id,
                "nome_cargo": fac_nome,
                "nome_fac": nome_fac,
                "fac_data": fac_data
            })
    
    return cargos_sem_lideres

# Função para atualizar informações dos líderes no banco
def atualizar_informacoes_lideres(fac_nome, membros_lideres, guild):
    """Atualiza quantidade e nomes dos líderes no banco de dados"""
    qtd_lideres = len(membros_lideres)  # Já é um inteiro
    
    if qtd_lideres > 0:
        nomes_lideres = "\n".join([f"• {membro.name} ({membro.id})" for membro in membros_lideres])
    else:
        nomes_lideres = "Nenhum líder encontrado"
    
    # Atualizar no banco de dados - AGORA qtd_lideres é INT
    cursor.execute("""
        UPDATE faccoes 
        SET qtd_lideres = ?, nomes_lideres = ?, ultima_verificacao = ?
        WHERE nome = ?
    """, (qtd_lideres, nomes_lideres, datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), fac_nome))
    db.commit()

# Tarefa periódica para verificar líderes (A CADA 10 MINUTOS)
@tasks.loop(minutes=10)
async def verificar_lideres_periodicamente():
    """Verifica periodicamente se há facções sem líderes"""
    print(f"🔍 [{datetime.datetime.now().strftime('%H:%M:%S')}] Iniciando verificação de líderes...")
    
    for guild in bot.guilds:
        try:
            cargos_sem_lideres = await verificar_lideres_no_servidor(guild)
            
            if cargos_sem_lideres:
                canal_painel = bot.get_channel(CANAL_PAINEL)
                if canal_painel:
                    embed = discord.Embed(
                        title="⚠️ ALERTA: FACÇÕES SEM LÍDERES DETECTADAS",
                        description=f"Foram encontradas {len(cargos_sem_lideres)} facções entregues sem líderes ativos:",
                        color=0xff9900,
                        timestamp=discord.utils.utcnow()
                    )
                    
                    for cargo_info in cargos_sem_lideres[:5]:
                        fac_data = cargo_info["fac_data"]
                        embed.add_field(
                            name=f"{cargo_info['nome_cargo']}",
                            value=f"**Facção:** {cargo_info['nome_fac']}\n"
                                  f"**Última verificação:** {datetime.datetime.now().strftime('%H:%M:%S')}",
                            inline=False
                        )
                    
                    if len(cargos_sem_lideres) > 5:
                        embed.add_field(
                            name="📋 Mais facções...",
                            value=f"Total de {len(cargos_sem_lideres)} facções sem líderes.",
                            inline=False
                        )
                    
                    embed.add_field(
                        name="📝 Ação Recomendada",
                        value="Considere recolher estas facções através do painel de controle.",
                        inline=False
                    )
                    
                    embed.set_footer(text="Verificação automática - A cada 10 minutos")
                    
                    mensagem = await canal_painel.send(embed=embed)
                    await mensagem.add_reaction("⚠️")
                    
                    print(f"✅ [{datetime.datetime.now().strftime('%H:%M:%S')}] Notificação enviada para {len(cargos_sem_lideres)} facções sem líderes")
                    
        except Exception as e:
            print(f"❌ [{datetime.datetime.now().strftime('%H:%M:%S')}] Erro na verificação periódica: {e}")

# Funções do banco de dados
def salvar_fac(nome, segmento, cds, termos, staff, lideres, status, motivo_recolhida=None, motivo_desativada=None):
    fac_existente = carregar_fac(nome)
    
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    data_entrega = data_atual
    data_recolhida = None
    data_desativada = None
    
    if fac_existente and fac_existente["status"] == "🟢 ENTREGUE":
        data_entrega = fac_existente["data"]
    
    if status == "🟡 RECOLHIDA":
        data_recolhida = data_atual
        if fac_existente:
            data_entrega = fac_existente["data"]
    elif status == "🔴 DESATIVADA":
        data_desativada = data_atual
        if fac_existente:
            data_entrega = fac_existente["data"]
            if fac_existente["data_recolhida"]:
                data_recolhida = fac_existente["data_recolhida"]
    
    if not motivo_recolhida and fac_existente:
        motivo_recolhida = fac_existente["motivo_recolhida"]
    if not motivo_desativada and fac_existente:
        motivo_desativada = fac_existente["motivo_desativada"]
    
    # Encontrar ID do cargo correspondente
    id_cargo_lider = obter_id_cargo_por_fac(nome)
    
    # Se já existe, manter qtd_lideres existente, senão iniciar com 0
    if fac_existente and "qtd_lideres" in fac_existente:
        qtd_lideres = fac_existente["qtd_lideres"]
    else:
        qtd_lideres = 0
    
    # Se já existe, manter nomes_lideres existente, senão iniciar
    if fac_existente and "nomes_lideres" in fac_existente:
        nomes_lideres = fac_existente["nomes_lideres"]
    else:
        nomes_lideres = "Aguardando verificação..."
    
    cursor.execute("""
        REPLACE INTO faccoes 
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        nome, segmento, cds, termos, staff, lideres, status,
        data_entrega, data_recolhida, data_desativada,
        motivo_recolhida, motivo_desativada,
        str(id_cargo_lider) if id_cargo_lider else None,
        data_atual, 
        qtd_lideres,  # ✅ AGORA É INT
        nomes_lideres
    ))
    db.commit()
    
    bot.loop.create_task(atualizar_painel())

def deletar_fac(nome):
    cursor.execute("DELETE FROM faccoes WHERE nome=?", (nome,))
    db.commit()
    
    bot.loop.create_task(atualizar_painel())

def carregar_fac(nome):
    cursor.execute("SELECT * FROM faccoes WHERE nome=?", (nome,))
    r = cursor.fetchone()
    if r: 
        return {
            "nome": r[0], "segmento": r[1], "cds": r[2], 
            "termos": r[3], "staff": r[4], "lideres": r[5], 
            "status": r[6], "data": r[7], "data_recolhida": r[8] if len(r) > 8 else None,
            "data_desativada": r[9] if len(r) > 9 else None, "motivo_recolhida": r[10] if len(r) > 10 else None,
            "motivo_desativada": r[11] if len(r) > 11 else None,
            "id_cargo_lider": r[12] if len(r) > 12 else None,
            "ultima_verificacao": r[13] if len(r) > 13 else None,
            "qtd_lideres": int(r[14]) if len(r) > 14 and r[14] is not None else 0,  # ✅ CONVERTE PARA INT
            "nomes_lideres": r[15] if len(r) > 15 else "Não verificado"
        }

def listar_fac():
    cursor.execute("SELECT nome FROM faccoes ORDER BY nome")
    return [x[0] for x in cursor.fetchall()]

def listar_fac_entregues():
    cursor.execute("SELECT nome FROM faccoes WHERE status=? ORDER BY nome", ("🟢 ENTREGUE",))
    return [x[0] for x in cursor.fetchall()]

def listar_fac_recolhidas():
    cursor.execute("SELECT nome FROM faccoes WHERE status=? ORDER BY nome", ("🟡 RECOLHIDA",))
    return [x[0] for x in cursor.fetchall()]

def listar_fac_desativadas():
    cursor.execute("SELECT nome FROM faccoes WHERE status=? ORDER BY nome", ("🔴 DESATIVADA",))
    return [x[0] for x in cursor.fetchall()]

def listar_fac_para_reentrega():
    cursor.execute("SELECT nome FROM faccoes WHERE status=? OR status=? ORDER BY nome", 
                   ("🟡 RECOLHIDA", "🔴 DESATIVADA"))
    return [x[0] for x in cursor.fetchall()]

def listar_fac_para_desativar():
    cursor.execute("SELECT nome FROM faccoes WHERE status=? OR status=? ORDER BY nome", 
                   ("🟢 ENTREGUE", "🟡 RECOLHIDA"))
    return [x[0] for x in cursor.fetchall()]

def contar_faccoes():
    cursor.execute("SELECT status, COUNT(*) FROM faccoes GROUP BY status")
    resultado = cursor.fetchall()
    contagem = {"🟢 ENTREGUE": 0, "🟡 RECOLHIDA": 0, "🔴 DESATIVADA": 0}
    for status, count in resultado:
        if status in contagem:
            contagem[status] = count
    return contagem

def listar_fac_por_status(status):
    cursor.execute("SELECT nome FROM faccoes WHERE status=? ORDER BY nome", (status,))
    return [x[0] for x in cursor.fetchall()]

def dividir_em_paginas(lista, itens_por_pagina=25):
    return [lista[i:i + itens_por_pagina] for i in range(0, len(lista), itens_por_pagina)]

# Atualizar informações dos líderes para todas as facções
async def atualizar_todas_lideres():
    """Atualiza informações de líderes para todas as facções"""
    for guild in bot.guilds:
        for fac_nome in listar_fac_entregues():
            id_cargo = obter_id_cargo_por_fac(fac_nome)
            if id_cargo:
                cargo = guild.get_role(id_cargo)
                if cargo:
                    membros_com_cargo = [membro for membro in guild.members if cargo in membro.roles]
                    atualizar_informacoes_lideres(fac_nome, membros_com_cargo, guild)

async def atualizar_painel():
    canal = bot.get_channel(CANAL_PAINEL)
    if not canal:
        return
    
    async for message in canal.history(limit=10):
        if message.author == bot.user and message.components:
            contagem = contar_faccoes()
            
            # Verificar facções sem líderes
            faccoes_sem_lideres = []
            for guild in bot.guilds:
                cargos_sem_lideres = await verificar_lideres_no_servidor(guild)
                faccoes_sem_lideres.extend([c["nome_fac"] for c in cargos_sem_lideres])
            
            embed = discord.Embed(
                title="📊 PAINEL DE CONTROLE DE FACÇÕES",
                description=f"**Status atual das facções**\n"
                           f"⏰ **Verificação automática:** A cada 10 minutos\n"
                           f"⚠️ **Facções sem líderes:** {len(faccoes_sem_lideres)}",
                color=0x7289da,
                timestamp=discord.utils.utcnow()
            )
            
            embed.set_image(url="https://i.ibb.co/j9PhvJCp/image.png")
            
            entregues = listar_fac_por_status('🟢 ENTREGUE')
            recolhidas = listar_fac_por_status('🟡 RECOLHIDA')
            desativadas = listar_fac_por_status('🔴 DESATIVADA')
            
            embed.add_field(
                name="📤 FACÇÕES ENTREGUES",
                value=f"**Quantidade:** {contagem['🟢 ENTREGUE']}\n**Facções:** {', '.join(entregues[:10])}{'...' if len(entregues) > 10 else ''}",
                inline=False
            )
            embed.add_field(
                name="📥 FACÇÕES RECOLHIDAS/DISPONÍVEIS", 
                value=f"**Quantidade:** {contagem['🟡 RECOLHIDA']}\n**Facções:** {', '.join(recolhidas[:10])}{'...' if len(recolhidas) > 10 else ''}",
                inline=False
            )
            embed.add_field(
                name="⛔ FACÇÕES DESATIVADAS",
                value=f"**Quantidade:** {contagem['🔴 DESATIVADA']}\n**Facções:** {', '.join(desativadas[:10])}{'...' if len(desativadas) > 10 else ''}",
                inline=False
            )
            
            if faccoes_sem_lideres:
                embed.add_field(
                    name="🚨 ALERTA: FACÇÕES SEM LÍDERES",
                    value=f"**Facções:** {', '.join(faccoes_sem_lideres[:5])}{'...' if len(faccoes_sem_lideres) > 5 else ''}\n"
                          f"**Última verificação:** {datetime.datetime.now().strftime('%H:%M:%S')}",
                    inline=False
                )
            
            embed.set_footer(text=f"Atualizado em • Próxima verificação em 10 minutos")
            
            try:
                await message.edit(embed=embed, view=Painel())
            except:
                pass
            break

@bot.event
async def on_ready():
    print(f"🔥 BOT ONLINE {bot.user}")
    
    # Iniciar verificação periódica (a cada 10 minutos)
    verificar_lideres_periodicamente.start()
    print("✅ Verificação periódica iniciada (a cada 10 minutos)")
    
    # Atualizar informações de líderes ao iniciar
    await atualizar_todas_lideres()
    print("✅ Informações de líderes atualizadas")
    
    canal = bot.get_channel(CANAL_PAINEL)
    if canal:
        async for message in canal.history(limit=10):
            if message.author == bot.user and message.components:
                print("✅ Painel já existe")
                return
        
        # Criar painel inicial
        contagem = contar_faccoes()
        embed = discord.Embed(
            title="📊 PAINEL DE CONTROLE DE FACÇÕES",
            description="**Sistema de gerenciamento de facções**\n\n"
                       "⏰ **Verificação automática:** A cada 10 minutos\n"
                       "👑 **Monitoramento de líderes:** Ativo",
            color=0x7289da,
            timestamp=discord.utils.utcnow()
        )
        
        embed.set_image(url="https://i.ibb.co/j9PhvJCp/image.png")
        
        entregues = listar_fac_por_status('🟢 ENTREGUE')
        recolhidas = listar_fac_por_status('🟡 RECOLHIDA')
        desativadas = listar_fac_por_status('🔴 DESATIVADA')
        
        embed.add_field(
            name="📤 FACÇÕES ENTREGUES",
            value=f"**Quantidade:** {contagem['🟢 ENTREGUE']}\n**Facções:** {', '.join(entregues[:10])}{'...' if len(entregues) > 10 else ''}",
            inline=False
        )
        embed.add_field(
            name="📥 FACÇÕES RECOLHidas/DISPONÍVEIS", 
            value=f"**Quantidade:** {contagem['🟡 RECOLHIDA']}\n**Facções:** {', '.join(recolhidas[:10])}{'...' if len(recolhidas) > 10 else ''}",
            inline=False
        )
        embed.add_field(
            name="⛔ FACÇÕES DESATIVADAS",
            value=f"**Quantidade:** {contagem['🔴 DESATIVADA']}\n**Facções:** {', '.join(desativadas[:10])}{'...' if len(desativadas) > 10 else ''}",
            inline=False
        )
        embed.set_footer(text="Atualizado em")
        
        await canal.send(embed=embed, view=Painel())
        print("✅ Painel criado com sucesso!")

#=========================================
class Painel(discord.ui.View):
    def __init__(self): 
        super().__init__(timeout=None)
        
    @discord.ui.button(label="📤 ENTREGAR FAC", style=discord.ButtonStyle.primary)
    async def entregar(self,interaction,_):
        await interaction.response.send_message(
            "🔍 **Esta é uma facção nova ou uma reentrega?**\n\n"
            "• **NOVA FACÇÃO**: Facção que nunca foi registrada antes\n"
            "• **ENTREGAR FAC EXISTENTE/LIVRE**: Facção que estava recolhida/desativada e está sendo entregue novamente",
            view=SelecionarTipoEntrega(),
            ephemeral=True
        )

    @discord.ui.button(label="📥 RECOLHER FAC", style=discord.ButtonStyle.success)
    async def recolher(self,interaction,_):
        faccoes_entregues = listar_fac_entregues()
        if not faccoes_entregues:
            await interaction.response.send_message("❌ Nenhuma facção entregue disponível para recolhimento!", ephemeral=True)
            return
        
        if len(faccoes_entregues) <= 25:
            await interaction.response.send_message("Selecione a facção para recolher:", view=SelectFacRecolher(0), ephemeral=True)
        else:
            await interaction.response.send_message("Selecione a página e depois a facção para recolher:", view=PaginaRecolher(0), ephemeral=True)

    @discord.ui.button(label="⛔ DESATIVAR FAC", style=discord.ButtonStyle.danger)
    async def desativar(self,interaction,_):
        faccoes_para_desativar = listar_fac_para_desativar()
        if not faccoes_para_desativar:
            await interaction.response.send_message("❌ Nenhuma facção disponível para desativação!", ephemeral=True)
            return
        
        if len(faccoes_para_desativar) <= 25:
            await interaction.response.send_message("Selecione a facção para desativar:", view=SelectFacDesativar(0), ephemeral=True)
        else:
            await interaction.response.send_message("Selecione a página e depois a facção para desativar:", view=PaginaDesativar(0), ephemeral=True)

    @discord.ui.button(label="📊 STATUS FACÇÕES", style=discord.ButtonStyle.secondary)
    async def status(self,interaction,_):
        faccoes = listar_fac()
        if not faccoes: 
            return await interaction.response.send_message("⚠ Nenhuma fac encontrada!",ephemeral=True)
        
        if len(faccoes) <= 25:
            await interaction.response.send_message("Selecione uma fac:", view=MenuStatus(0), ephemeral=True)
        else:
            await interaction.response.send_message("Selecione a página e depois a facção:", view=PaginaStatus(0), ephemeral=True)

    @discord.ui.button(label="🔄 ATUALIZAR PAINEL", style=discord.ButtonStyle.blurple)
    async def atualizar(self, interaction, _):
        await atualizar_painel()
        await interaction.response.send_message("✅ Painel atualizado!", ephemeral=True)

    @discord.ui.button(label="📋 MOSTRAR FAC LIVRE", style=discord.ButtonStyle.green)
    async def mostrar_fac_livre(self, interaction, _):
        faccoes_recolhidas = listar_fac_recolhidas()
        
        if not faccoes_recolhidas:
            await interaction.response.send_message("❌ Nenhuma facção disponível para reentrega no momento!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 FACÇÕES DISPONÍVEIS PARA REENTREGA",
            description="Lista de facções recolhidas que estão disponíveis para reentrega:",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        for fac_nome in faccoes_recolhidas:
            fac_data = carregar_fac(fac_nome)
            embed.add_field(
                name=f"🟡 {fac_nome}",
                value=f"**Segmento:** {fac_data['segmento']}\n**Motivo da recolha:** {fac_data['motivo_recolhida'] or 'Não especificado'}\n**Data da recolha:** {fac_data['data_recolhida'] or 'Data não registrada'}",
                inline=False
            )
        
        embed.set_footer(text=f"Total de {len(faccoes_recolhidas)} facções disponíveis")
        
        await interaction.response.send_message(
            embed=embed,
            view=NotificarFacLivreView(faccoes_recolhidas),
            ephemeral=True
        )

    @discord.ui.button(label="🔍 VERIFICAR LÍDERES", style=discord.ButtonStyle.red, row=1)
    async def verificar_lideres(self, interaction, _):
        """Verificação manual de líderes"""
        await interaction.response.defer(ephemeral=True)
        
        for guild in bot.guilds:
            cargos_sem_lideres = await verificar_lideres_no_servidor(guild)
            
            if cargos_sem_lideres:
                embed = discord.Embed(
                    title="⚠️ VERIFICAÇÃO MANUAL - FACÇÕES SEM LÍDERES",
                    description=f"Foram encontradas {len(cargos_sem_lideres)} facções sem líderes:",
                    color=0xff9900,
                    timestamp=discord.utils.utcnow()
                )
                
                for cargo_info in cargos_sem_lideres[:5]:
                    embed.add_field(
                        name=f"• {cargo_info['nome_fac']}",
                        value=f"Cargo: {cargo_info['nome_cargo']}\nID: {cargo_info['id_cargo']}",
                        inline=False
                    )
                
                if len(cargos_sem_lideres) > 5:
                    embed.add_field(
                        name="Mais facções...",
                        value=f"Total: {len(cargos_sem_lideres)} facções sem líderes",
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send("✅ Todas as facções têm líderes ativos!", ephemeral=True)

#=========================================
class NotificarFacLivreView(discord.ui.View):
    def __init__(self, faccoes_recolhidas):
        super().__init__(timeout=120)
        self.faccoes_recolhidas = faccoes_recolhidas

    @discord.ui.button(label="🔔 NOTIFICAR FACÇÕES LIVRES", style=discord.ButtonStyle.primary)
    async def notificar_faccoes(self, interaction, button):
        """Envia notificação sobre as facções disponíveis"""
        if not self.faccoes_recolhidas:
            await interaction.response.send_message("❌ Nenhuma facção disponível para notificação!", ephemeral=True)
            return
        
        # Criar mensagem de notificação
        faccoes_lista = "\n".join([f"• **{fac}**" for fac in self.faccoes_recolhidas])
        
        embed = discord.Embed(
            title="🔔 NOTIFICAÇÃO - FACÇÕES DISPONÍVEIS",
            description=f"**{len(self.faccoes_recolhidas)} facções estão disponíveis para reentrega!**\n\n{faccoes_lista}",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="📝 COMO SOLICITAR",
            value="Use o botão **📤 ENTREGAR FAC** no painel e selecione **ENTREGAR FAC EXISTENTE/LIVRE** para solicitar uma destas facções.",
            inline=False
        )
        embed.set_footer(text="Sistema de Gerenciamento de Facções")
        
        # Enviar para o canal de notificação específico
        canal_notificacao = bot.get_channel(CANAL_NOTIFICACAO)
        if canal_notificacao:
            # MENCIONAR O USUÁRIO QUE CLICOU
            mensagem_conteudo = f"🔔 {interaction.user.mention} notificou sobre facções disponíveis!"
            await canal_notificacao.send(content=mensagem_conteudo, embed=embed)
            print(f"✅ Notificação enviada para o canal {CANAL_NOTIFICACAO} com {len(self.faccoes_recolhidas)} facções")
        else:
            print(f"❌ Canal de notificação {CANAL_NOTIFICACAO} não encontrado")
        
        # Confirmar para o usuário
        await interaction.response.edit_message(
            content=f"✅ Notificação enviada com {len(self.faccoes_recolhidas)} facções disponíveis!",
            embed=None,
            view=None
        )

    @discord.ui.button(label="❌ FECHAR", style=discord.ButtonStyle.danger)
    async def fechar(self, interaction, button):
        """Fecha a visualização das facções livres"""
        await interaction.response.edit_message(
            content="📋 Visualização de facções livres fechada.",
            embed=None,
            view=None
        )

#=========================================
class SelecionarTipoEntrega(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        
    @discord.ui.button(label="🆕 NOVA FACÇÃO", style=discord.ButtonStyle.primary, emoji="🆕")
    async def nova_faccao(self, interaction, button):
        await interaction.response.send_message("Escolha o segmento:", view=SelectSegmento("nova"), ephemeral=True)
        
    @discord.ui.button(label="📦 ENTREGAR FAC EXISTENTE/LIVRE", style=discord.ButtonStyle.success, emoji="📦")
    async def entregar_existente(self, interaction, button):
        faccoes_para_reentrega = listar_fac_para_reentrega()
        if not faccoes_para_reentrega:
            await interaction.response.send_message("❌ Nenhuma facção recolhida ou desativada disponível para reentrega!", ephemeral=True)
            return
        
        # Verificar se precisa de paginação para reentregas
        if len(faccoes_para_reentrega) <= 25:
            await interaction.response.send_message("Selecione a facção para reentregar:", view=SelectFacReentrega(), ephemeral=True)
        else:
            await interaction.response.send_message("Selecione a página e depois a facção para reentregar:", view=PaginaReentrega(0), ephemeral=True)

#=========================================
class SelectSegmento(discord.ui.View):
    def __init__(self, tipo="nova"):
        super().__init__(timeout=120)
        self.tipo = tipo
        self.select = discord.ui.Select(placeholder="Escolha segmento",
        options=[
            discord.SelectOption(label="🔫 Armas"),
            discord.SelectOption(label="💣 Munição"),
            discord.SelectOption(label="🧪 Lavagem"),
            discord.SelectOption(label="💊 Drogas")
        ])
        self.select.callback=self.callback
        self.add_item(self.select)

    async def callback(self,interaction):
        if self.tipo == "nova":
            await interaction.response.send_modal(EntregarFac(self.select.values[0], "nova"))

#=========================================
# VIEW DE PAGINAÇÃO PARA REENTREGA
class PaginaReentrega(discord.ui.View):
    def __init__(self, pagina_atual=0):
        super().__init__(timeout=120)
        self.pagina_atual = pagina_atual
        faccoes_para_reentrega = listar_fac_para_reentrega()
        self.paginas = dividir_em_paginas(faccoes_para_reentrega)
        
        # Adicionar botões de navegação
        if len(self.paginas) > 1:
            if self.pagina_atual > 0:
                self.add_item(BotaoPaginaAnteriorReentrega())
            if self.pagina_atual < len(self.paginas) - 1:
                self.add_item(BotaoPaginaProximaReentrega())
        
        # Adicionar select da página atual com indicação do status
        options = []
        for fac in self.paginas[self.pagina_atual]:
            fac_data = carregar_fac(fac)
            status_emoji = "🟡" if fac_data["status"] == "🟡 RECOLHIDA" else "🔴"
            options.append(discord.SelectOption(
                label=fac, 
                description=f"{status_emoji} {fac_data['status']}",
                value=fac
            ))
        
        self.select = discord.ui.Select(
            placeholder=f"Página {self.pagina_atual + 1} - Selecione a facção",
            options=options
        )
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction):
        fac_selecionada = self.select.values[0]
        fac_data = carregar_fac(fac_selecionada)
        
        # MODIFICAÇÃO: VAI DIRETAMENTE PARA O MODAL SEM SELECIONAR SEGMENTO
        await interaction.response.send_modal(ReentregarFac(fac_selecionada, fac_data))

class BotaoPaginaAnteriorReentrega(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="◀ Página Anterior", row=1)
    
    async def callback(self, interaction):
        view = self.view
        await interaction.response.edit_message(
            content="Selecione a página e depois a facção para reentregar:",
            view=PaginaReentrega(view.pagina_atual - 1)
        )

class BotaoPaginaProximaReentrega(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Próxima Página ▶", row=1)
    
    async def callback(self, interaction):
        view = self.view
        await interaction.response.edit_message(
            content="Selecione a página e depois a facção para reentregar:",
            view=PaginaReentrega(view.pagina_atual + 1)
        )

class SelectFacReentrega(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        faccoes_para_reentrega = listar_fac_para_reentrega()
        
        # Criar options com indicação do status
        options = []
        for fac in faccoes_para_reentrega:
            fac_data = carregar_fac(fac)
            status_emoji = "🟡" if fac_data["status"] == "🟡 RECOLHIDA" else "🔴"
            options.append(discord.SelectOption(
                label=fac, 
                description=f"{status_emoji} {fac_data['status']}",
                value=fac
            ))
        
        self.select = discord.ui.Select(
            placeholder="Selecione a facção para reentregar", 
            options=options
        )
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction):
        fac_selecionada = self.select.values[0]
        fac_data = carregar_fac(fac_selecionada)
        
        # MODIFICAÇÃO: VAI DIRETAMENTE PARA O MODAL SEM SELECIONAR SEGMENTO
        await interaction.response.send_modal(ReentregarFac(fac_selecionada, fac_data))

#=========================================
class ReentregarFac(discord.ui.Modal,title="🔄 Reentregar FAC"):
    def __init__(self, fac_nome, fac_atual):
        super().__init__()
        self.fac_nome = fac_nome
        self.segmento = fac_atual["segmento"]  # ✅ MANTÉM O SEGMENTO ORIGINAL
        
        # Definir os campos do modal
        self.nome = discord.ui.TextInput(label="Nome da FAC", default=fac_atual["nome"], required=True)
        self.cds = discord.ui.TextInput(label="CDS", default=fac_atual["cds"], required=True)
        self.termos = discord.ui.TextInput(label="Termos", default=fac_atual["termos"], required=True)
        self.staff = discord.ui.TextInput(label="Staff Responsável", default=fac_atual["staff"], required=True)
        self.lideres = discord.ui.TextInput(label="Líderes", style=discord.TextStyle.paragraph, default=fac_atual["lideres"], required=True)

        for i in (self.nome, self.cds, self.termos, self.staff, self.lideres):
            self.add_item(i)

    async def on_submit(self,interaction):
        # Salvar como entregue, mantendo o segmento original e dados históricos
        salvar_fac(
            self.nome.value,
            self.segmento,  # ✅ MANTÉM O SEGMENTO ORIGINAL (NÃO PODE SER ALTERADO)
            self.cds.value,
            self.termos.value,
            self.staff.value,
            self.lideres.value,
            "🟢 ENTREGUE"   # Status atualizado para entregue
        )

        # Determinar o status anterior para o embed
        fac_data_anterior = carregar_fac(self.fac_nome)  # Carregar dados antigos
        status_anterior = fac_data_anterior["status"] if fac_data_anterior else "DESCONHECIDO"
        tipo_reentrega = "RECOLHIDA" if status_anterior == "🟡 RECOLHIDA" else "DESATIVADA"
        
        # ENVIAR PARA CANAL DE ENTREGUES - COM STAFF E USUÁRIO FORA DO EMBED
        embed = discord.Embed(
            title=f"🔄 FACÇÃO REENTREGUE: {self.nome.value}",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="SEGMENTO", value=self.segmento, inline=True)
        embed.add_field(name="CDS", value=self.cds.value, inline=True)
        embed.add_field(name="TERMOS", value=self.termos.value, inline=True)
        embed.add_field(name="LÍDERES", value=self.lideres.value, inline=False)
        embed.add_field(name="STATUS", value="🟢 ENTREGUE", inline=True)
        embed.add_field(name="TIPO", value=f"🔄 REENTREGA ({tipo_reentrega})", inline=True)
        embed.add_field(name="📝 HISTÓRICO", value=f"Facção estava {status_anterior.lower()} anteriormente", inline=False)
        embed.set_footer(text=f"Reentregue em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        canal_entregues = bot.get_channel(CANAL_ENTREGUES)
        if canal_entregues:
            # Enviar mensagem com staff responsável e usuário que clicou
            mensagem_conteudo = (
                f"**👤 STAFF RESPONSÁVEL:** {self.staff.value}\n"
                f"**🎮 SOLICITADO POR:** {interaction.user.mention}"
            )
            await canal_entregues.send(content=mensagem_conteudo, embed=embed)
            print(f"✅ Facção {self.nome.value} reentregue no canal de entregues")

        await interaction.response.send_message(
            f"🔄 FAC Reentregada com sucesso!\n"
            f"**Status anterior:** {status_anterior}\n"
            f"**Segmento mantido:** {self.segmento}",
            ephemeral=True
        )

#=========================================
class EntregarFac(discord.ui.Modal,title="📤 Registrar FAC (Nova)"):
    def __init__(self, segmento, tipo="nova"):
        super().__init__()
        self.segmento = segmento
        self.tipo = tipo
        self.nome = discord.ui.TextInput(label="Nome da FAC")
        self.cds = discord.ui.TextInput(label="CDS")
        self.termos = discord.ui.TextInput(label="Termos")
        self.staff = discord.ui.TextInput(label="Staff Responsável")
        self.lideres = discord.ui.TextInput(label="Líderes", style=discord.TextStyle.paragraph)

        for i in (self.nome, self.cds, self.termos, self.staff, self.lideres):
            self.add_item(i)

    async def on_submit(self,interaction):
        salvar_fac(self.nome.value, self.segmento, self.cds.value, self.termos.value,
                   self.staff.value, self.lideres.value, "🟢 ENTREGUE")

        # ENVIAR PARA CANAL DE ENTREGUES - COM STAFF E USUÁRIO FORA DO EMBED
        embed = discord.Embed(
            title=f"📤 FACÇÃO ENTREGUE: {self.nome.value}",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="SEGMENTO", value=self.segmento, inline=True)
        embed.add_field(name="CDS", value=self.cds.value, inline=True)
        embed.add_field(name="TERMOS", value=self.termos.value, inline=True)
        embed.add_field(name="LÍDERES", value=self.lideres.value, inline=False)
        embed.add_field(name="STATUS", value="🟢 ENTREGUE", inline=True)
        embed.add_field(name="TIPO", value="🆕 NOVA FACÇÃO", inline=True)
        embed.set_footer(text=f"Registrado em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        canal_entregues = bot.get_channel(CANAL_ENTREGUES)
        if canal_entregues:
            # Enviar mensagem com staff responsável e usuário que clicou
            mensagem_conteudo = (
                f"**👤 STAFF RESPONSÁVEL:** {self.staff.value}\n"
                f"**🎮 SOLICITADO POR:** {interaction.user.mention}"
            )
            await canal_entregues.send(content=mensagem_conteudo, embed=embed)
            print(f"✅ Nova facção {self.nome.value} enviada para canal de entregues")

        await interaction.response.send_message("✔ FAC registrada!", ephemeral=True)

#=========================================
# VIEWS DE PAGINAÇÃO PARA RECOLHER
class PaginaRecolher(discord.ui.View):
    def __init__(self, pagina_atual=0):
        super().__init__(timeout=120)
        self.pagina_atual = pagina_atual
        faccoes_entregues = listar_fac_entregues()
        self.paginas = dividir_em_paginas(faccoes_entregues)
        
        # Adicionar botões de navegação
        if len(self.paginas) > 1:
            if self.pagina_atual > 0:
                self.add_item(BotaoPaginaAnteriorRecolher())
            if self.pagina_atual < len(self.paginas) - 1:
                self.add_item(BotaoPaginaProximaRecolher())
        
        # Adicionar select da página atual
        options = [
            discord.SelectOption(label=fac, value=fac) 
            for fac in self.paginas[self.pagina_atual]
        ]
        
        self.select = discord.ui.Select(
            placeholder=f"Página {self.pagina_atual + 1} - Selecione a facção (Ordem Alfabética)",
            options=options
        )
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction):
        fac_selecionada = self.select.values[0]
        await interaction.response.send_modal(RecolherFacModal(fac_selecionada))

class BotaoPaginaAnteriorRecolher(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="◀ Página Anterior", row=1)
    
    async def callback(self, interaction):
        view = self.view
        await interaction.response.edit_message(
            content="Selecione a página e depois a facção para recolher:",
            view=PaginaRecolher(view.pagina_atual - 1)
        )

class BotaoPaginaProximaRecolher(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Próxima Página ▶", row=1)
    
    async def callback(self, interaction):
        view = self.view
        await interaction.response.edit_message(
            content="Selecione a página e depois a facção para recolher:",
            view=PaginaRecolher(view.pagina_atual + 1)
        )

class SelectFacRecolher(discord.ui.View):
    def __init__(self, pagina=0):
        super().__init__(timeout=120)
        faccoes_entregues = listar_fac_entregues()
        options = [discord.SelectOption(label=fac) for fac in faccoes_entregues]
        
        self.select = discord.ui.Select(
            placeholder="Selecione a facção para recolher (Ordem Alfabética)", 
            options=options
        )
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction):
        fac_selecionada = self.select.values[0]
        await interaction.response.send_modal(RecolherFacModal(fac_selecionada))

class RecolherFacModal(discord.ui.Modal):
    def __init__(self, fac_nome):
        super().__init__(title="📥 Registrar FAC Recolhida", timeout=None)
        self.fac_nome = fac_nome
        self.staff = discord.ui.TextInput(label="Staff responsável", required=True)
        self.motivo = discord.ui.TextInput(label="Motivo", style=discord.TextStyle.paragraph, required=True)
        
        self.add_item(self.staff)
        self.add_item(self.motivo)

    async def on_submit(self,interaction):
        # Carregar dados atuais da facção para manter CDS e outras informações
        fac_atual = carregar_fac(self.fac_nome)
        
        salvar_fac(
            self.fac_nome,
            fac_atual["segmento"],  # Mantém o segmento original
            fac_atual["cds"],       # ✅ MANTÉM A CDS ORIGINAL
            fac_atual["termos"],    # Mantém os termos originais
            self.staff.value,       # Novo staff responsável
            fac_atual["lideres"],   # Mantém os líderes originais
            "🟡 RECOLHIDA",         # Novo status
            motivo_recolhida=self.motivo.value  # ✅ SALVA O MOTIVO
        )
        
        # ENVIAR PARA CANAL DE RECOLHIDAS - COM STAFF E USUÁRIO FORA DO EMBED
        embed = discord.Embed(
            title=f"📥 FACÇÃO RECOLHIDA: {self.fac_nome}",
            color=0xffff00,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="SEGMENTO", value=fac_atual["segmento"], inline=True)
        embed.add_field(name="CDS", value=fac_atual["cds"], inline=True)  # ✅ CDS MANTIDA
        embed.add_field(name="TERMOS", value=fac_atual["termos"], inline=True)
        embed.add_field(name="LÍDERES", value=fac_atual["lideres"], inline=False)
        embed.add_field(name="MOTIVO", value=self.motivo.value, inline=False)
        embed.add_field(name="STATUS", value="🟡 RECOLHIDA", inline=True)
        embed.set_footer(text=f"Recolhida em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        canal_recolhidas = bot.get_channel(CANAL_RECOLHIDAS)
        if canal_recolhidas:
            # Enviar mensagem com staff responsável e usuário que clicou
            mensagem_conteudo = (
                f"**👤 STAFF RESPONSÁVEL:** {self.staff.value}\n"
                f"**🎮 SOLICITADO POR:** {interaction.user.mention}"
            )
            await canal_recolhidas.send(content=mensagem_conteudo, embed=embed)
            print(f"✅ Facção {self.fac_nome} enviada para canal de recolhidas")

        await interaction.response.send_message("📥 FAC Recolhida Registrada!",ephemeral=True)

#=========================================
# VIEWS DE PAGINAÇÃO PARA DESATIVAR
class PaginaDesativar(discord.ui.View):
    def __init__(self, pagina_atual=0):
        super().__init__(timeout=120)
        self.pagina_atual = pagina_atual
        faccoes_para_desativar = listar_fac_para_desativar()
        self.paginas = dividir_em_paginas(faccoes_para_desativar)
        
        # Adicionar botões de navegação
        if len(self.paginas) > 1:
            if self.pagina_atual > 0:
                self.add_item(BotaoPaginaAnteriorDesativar())
            if self.pagina_atual < len(self.paginas) - 1:
                self.add_item(BotaoPaginaProximaDesativar())
        
        # Adicionar select da página atual
        options = [
            discord.SelectOption(label=fac, value=fac) 
            for fac in self.paginas[self.pagina_atual]
        ]
        
        self.select = discord.ui.Select(
            placeholder=f"Página {self.pagina_atual + 1} - Selecione a facção (Ordem Alfabética)",
            options=options
        )
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction):
        fac_selecionada = self.select.values[0]
        await interaction.response.send_modal(DesativarFacModal(fac_selecionada))

class BotaoPaginaAnteriorDesativar(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="◀ Página Anterior", row=1)
    
    async def callback(self, interaction):
        view = self.view
        await interaction.response.edit_message(
            content="Selecione a página e depois a facção para desativar:",
            view=PaginaDesativar(view.pagina_atual - 1)
        )

class BotaoPaginaProximaDesativar(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Próxima Página ▶", row=1)
    
    async def callback(self, interaction):
        view = self.view
        await interaction.response.edit_message(
            content="Selecione a página e depois a facção para desativar:",
            view=PaginaDesativar(view.pagina_atual + 1)
        )

class SelectFacDesativar(discord.ui.View):
    def __init__(self, pagina=0):
        super().__init__(timeout=120)
        faccoes_para_desativar = listar_fac_para_desativar()
        options = [discord.SelectOption(label=fac) for fac in faccoes_para_desativar]
        
        self.select = discord.ui.Select(
            placeholder="Selecione a facção para desativar (Ordem Alfabética)", 
            options=options
        )
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction):
        fac_selecionada = self.select.values[0]
        await interaction.response.send_modal(DesativarFacModal(fac_selecionada))

class DesativarFacModal(discord.ui.Modal):
    def __init__(self, fac_nome):
        super().__init__(title="⛔ Desativar Facção", timeout=None)
        self.fac_nome = fac_nome
        self.staff = discord.ui.TextInput(label="Staff responsável", required=True)
        self.motivo = discord.ui.TextInput(label="Motivo", style=discord.TextStyle.paragraph, required=True)
        
        self.add_item(self.staff)
        self.add_item(self.motivo)

    async def on_submit(self,interaction):
        # Carregar dados atuais da facção para manter informações
        fac_atual = carregar_fac(self.fac_nome)
        
        salvar_fac(
            self.fac_nome,
            fac_atual["segmento"],  # Mantém o segmento original
            fac_atual["cds"],       # ✅ MANTÉM A CDS ORIGINAL
            fac_atual["termos"],    # Mantém os termos originais
            self.staff.value,       # Novo staff responsável
            fac_atual["lideres"],   # Mantém os líderes originais
            "🔴 DESATIVADA",        # Novo status
            motivo_desativada=self.motivo.value  # ✅ SALVA O MOTIVO
        )
        
        # ENVIAR PARA CANAL DE DESATIVADAS - COM STAFF E USUÁRIO FORA DO EMBED
        embed = discord.Embed(
            title=f"❌ FACÇÃO DESATIVADA: {self.fac_nome}",
            color=0xff0000,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="SEGMENTO", value=fac_atual["segmento"], inline=True)
        embed.add_field(name="CDS", value=fac_atual["cds"], inline=True)  # ✅ CDS MANTIDA
        embed.add_field(name="TERMOS", value=fac_atual["termos"], inline=True)
        embed.add_field(name="LÍDERES", value=fac_atual["lideres"], inline=False)
        embed.add_field(name="MOTIVO", value=self.motivo.value, inline=False)
        embed.add_field(name="STATUS", value="🔴 DESATIVADA", inline=True)
        embed.set_footer(text=f"Desativada em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        canal_desativadas = bot.get_channel(CANAL_DESATIVADAS)
        if canal_desativadas:
            # Enviar mensagem com staff responsável e usuário que clicou
            mensagem_conteudo = (
                f"**👤 STAFF RESPONSÁVEL:** {self.staff.value}\n"
                f"**🎮 SOLICITADO POR:** {interaction.user.mention}"
            )
            await canal_desativadas.send(content=mensagem_conteudo, embed=embed)
            print(f"✅ Facção {self.fac_nome} enviada para canal de desativadas")

        await interaction.response.send_message("❌ FAC Desativada!",ephemeral=True)

#=========================================
# VIEWS DE PAGINAÇÃO PARA STATUS
# MODIFICAÇÃO SIMILAR PARA PAGINA STATUS
class PaginaStatus(discord.ui.View):
    def __init__(self, pagina_atual=0):
        super().__init__(timeout=120)
        self.pagina_atual = pagina_atual
        faccoes = listar_fac()
        self.paginas = dividir_em_paginas(faccoes)
        
        if len(self.paginas) > 1:
            if self.pagina_atual > 0:
                self.add_item(BotaoPaginaAnteriorStatus())
            if self.pagina_atual < len(self.paginas) - 1:
                self.add_item(BotaoPaginaProximaStatus())
        
        options = [
            discord.SelectOption(label=fac, value=fac) 
            for fac in self.paginas[self.pagina_atual]
        ]
        
        self.select = discord.ui.Select(
            placeholder=f"Página {self.pagina_atual + 1} - Selecione a facção (Ordem Alfabética)",
            options=options
        )
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction):
        fac_selecionada = self.select.values[0]
        fac = carregar_fac(fac_selecionada)
        
        # Verificar líderes atuais - CONVERTER PARA INTEIRO
        qtd_lideres = int(fac.get("qtd_lideres", 0) or 0)  # ✅ CONVERTE PARA INT
        nomes_lideres = fac.get("nomes_lideres", "Não verificado")
        
        emb = discord.Embed(
            title=f"📊 FAC — {fac['nome']}",
            color=0x00ffff if fac['status'] == "🟢 ENTREGUE" else 
                  0xffff00 if fac['status'] == "🟡 RECOLHIDA" else 0xff0000
        )

        # Campos principais
        emb.add_field(name="NOME", value=fac['nome'], inline=True)
        emb.add_field(name="SEGMENTO", value=fac['segmento'], inline=True)
        emb.add_field(name="STATUS", value=fac['status'], inline=True)
        emb.add_field(name="CDS", value=fac['cds'], inline=False)
        emb.add_field(name="TERMOS", value=fac['termos'], inline=True)
        emb.add_field(name="STAFF", value=fac['staff'], inline=True)
        
        # Informações dos líderes
        if fac['status'] == "🟢 ENTREGUE":
            if qtd_lideres > 0:
                emb.add_field(
                    name=f"👑 LÍDERES ATUAIS ({qtd_lideres})",
                    value=nomes_lideres,
                    inline=False
                )
            else:
                emb.add_field(
                    name="⚠️ LÍDERES",
                    value="**NENHUM LÍDER ENCONTRADO**\nEsta facção está sem líderes ativos!",
                    inline=False
                )
        else:
            emb.add_field(name="LÍDERES REGISTRADOS", value=fac['lideres'], inline=False)
        
        # Datas importantes
        emb.add_field(name="📅 DATA DE ENTREGA", value=fac['data'], inline=True)
        emb.add_field(name="⏰ ÚLTIMA VERIFICAÇÃO", value=fac.get('ultima_verificacao', 'Não verificado'), inline=True)
        
        if fac['status'] == "🟡 RECOLHIDA" and fac['motivo_recolhida']:
            emb.add_field(name="📥 DATA DE RECOLHA", value=fac['data_recolhida'] or "Data não registrada", inline=True)
            emb.add_field(name="📝 MOTIVO DA RECOLHA", value=fac['motivo_recolhida'], inline=False)
        
        if fac['status'] == "🔴 DESATIVADA" and fac['motivo_desativada']:
            emb.add_field(name="❌ DATA DE DESATIVAÇÃO", value=fac['data_desativada'] or "Data não registrada", inline=True)
            emb.add_field(name="📝 MOTIVO DA DESATIVAÇÃO", value=fac['motivo_desativada'], inline=False)

        await interaction.response.send_message(embed=emb, view=StatusActions(fac["nome"]), ephemeral=True)

# MODIFICAÇÃO NA EXIBIÇÃO DO STATUS - AGORA MOSTRA LÍDERES
class StatusChoice(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Selecione uma facção (Ordem Alfabética)", options=options)

    async def callback(self,interaction):
        fac = carregar_fac(self.values[0])
        
        # Verificar líderes atuais - CONVERTER PARA INTEIRO
        id_cargo = obter_id_cargo_por_fac(fac["nome"])
        qtd_lideres = int(fac.get("qtd_lideres", 0) or 0)  # ✅ CONVERTE PARA INT
        nomes_lideres = fac.get("nomes_lideres", "Não verificado")
        
        emb = discord.Embed(
            title=f"📊 FAC — {fac['nome']}",
            color=0x00ffff if fac['status'] == "🟢 ENTREGUE" else 
                  0xffff00 if fac['status'] == "🟡 RECOLHIDA" else 0xff0000
        )

        # Campos principais
        emb.add_field(name="NOME", value=fac['nome'], inline=True)
        emb.add_field(name="SEGMENTO", value=fac['segmento'], inline=True)
        emb.add_field(name="STATUS", value=fac['status'], inline=True)
        emb.add_field(name="CDS", value=fac['cds'], inline=False)
        emb.add_field(name="TERMOS", value=fac['termos'], inline=True)
        emb.add_field(name="STAFF", value=fac['staff'], inline=True)
        
        # Informações dos líderes
        if fac['status'] == "🟢 ENTREGUE":
            if qtd_lideres > 0:
                emb.add_field(
                    name=f"👑 LÍDERES ATUAIS ({qtd_lideres})",
                    value=nomes_lideres,
                    inline=False
                )
            else:
                emb.add_field(
                    name="⚠️ LÍDERES",
                    value="**NENHUM LÍDER ENCONTRADO**\nEsta facção está sem líderes ativos!",
                    inline=False
                )
        else:
            emb.add_field(name="LÍDERES REGISTRADOS", value=fac['lideres'], inline=False)
        
        # Datas importantes
        emb.add_field(name="📅 DATA DE ENTREGA", value=fac['data'], inline=True)
        emb.add_field(name="⏰ ÚLTIMA VERIFICAÇÃO", value=fac.get('ultima_verificacao', 'Não verificado'), inline=True)
        
        if fac['status'] == "🟡 RECOLHIDA" and fac['motivo_recolhida']:
            emb.add_field(name="📥 DATA DE RECOLHA", value=fac['data_recolhida'] or "Data não registrada", inline=True)
            emb.add_field(name="📝 MOTIVO DA RECOLHA", value=fac['motivo_recolhida'], inline=False)
        
        if fac['status'] == "🔴 DESATIVADA" and fac['motivo_desativada']:
            emb.add_field(name="❌ DATA DE DESATIVAÇÃO", value=fac['data_desativada'] or "Data não registrada", inline=True)
            emb.add_field(name="📝 MOTIVO DA DESATIVAÇÃO", value=fac['motivo_desativada'], inline=False)

        await interaction.response.send_message(embed=emb, view=StatusActions(fac["nome"]), ephemeral=True)
        

class BotaoPaginaAnteriorStatus(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="◀ Página Anterior", row=1)
    
    async def callback(self, interaction):
        view = self.view
        await interaction.response.edit_message(
            content="Selecione a página e depois a facção:",
            view=PaginaStatus(view.pagina_atual - 1)
        )

class BotaoPaginaProximaStatus(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Próxima Página ▶", row=1)
    
    async def callback(self, interaction):
        view = self.view
        await interaction.response.edit_message(
            content="Selecione a página e depois a facção:",
            view=PaginaStatus(view.pagina_atual + 1)
        )

class MenuStatus(discord.ui.View):
    def __init__(self, pagina=0):
        super().__init__(timeout=600)
        faccoes = listar_fac()
        options = [discord.SelectOption(label=f) for f in faccoes]
        self.select = StatusChoice(options=options)
        self.add_item(self.select)

class StatusChoice(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Selecione uma facção (Ordem Alfabética)", options=options)

    async def callback(self,interaction):
        fac = carregar_fac(self.values[0])
        
        # Verificar líderes atuais
        id_cargo = obter_id_cargo_por_fac(fac["nome"])
        qtd_lideres = fac.get("qtd_lideres", 0)
        nomes_lideres = fac.get("nomes_lideres", "Não verificado")
        
        emb = discord.Embed(
            title=f"📊 FAC — {fac['nome']}",
            color=0x00ffff if fac['status'] == "🟢 ENTREGUE" else 
                  0xffff00 if fac['status'] == "🟡 RECOLHIDA" else 0xff0000
        )

        # Campos principais
        emb.add_field(name="NOME", value=fac['nome'], inline=True)
        emb.add_field(name="SEGMENTO", value=fac['segmento'], inline=True)
        emb.add_field(name="STATUS", value=fac['status'], inline=True)
        emb.add_field(name="CDS", value=fac['cds'], inline=False)
        emb.add_field(name="TERMOS", value=fac['termos'], inline=True)
        emb.add_field(name="STAFF", value=fac['staff'], inline=True)
        
        # Informações dos líderes
        if fac['status'] == "🟢 ENTREGUE":
            if qtd_lideres > 0:
                emb.add_field(
                    name=f"👑 LÍDERES ATUAIS ({qtd_lideres})",
                    value=nomes_lideres,
                    inline=False
                )
            else:
                emb.add_field(
                    name="⚠️ LÍDERES",
                    value="**NENHUM LÍDER ENCONTRADO**\nEsta facção está sem líderes ativos!",
                    inline=False
                )
        else:
            emb.add_field(name="LÍDERES REGISTRADOS", value=fac['lideres'], inline=False)
        
        # Datas importantes
        emb.add_field(name="📅 DATA DE ENTREGA", value=fac['data'], inline=True)
        emb.add_field(name="⏰ ÚLTIMA VERIFICAÇÃO", value=fac.get('ultima_verificacao', 'Não verificado'), inline=True)
        
        if fac['status'] == "🟡 RECOLHIDA" and fac['motivo_recolhida']:
            emb.add_field(name="📥 DATA DE RECOLHA", value=fac['data_recolhida'] or "Data não registrada", inline=True)
            emb.add_field(name="📝 MOTIVO DA RECOLHA", value=fac['motivo_recolhida'], inline=False)
        
        if fac['status'] == "🔴 DESATIVADA" and fac['motivo_desativada']:
            emb.add_field(name="❌ DATA DE DESATIVAÇÃO", value=fac['data_desativada'] or "Data não registrada", inline=True)
            emb.add_field(name="📝 MOTIVO DA DESATIVAÇÃO", value=fac['motivo_desativada'], inline=False)

        await interaction.response.send_message(embed=emb, view=StatusActions(fac["nome"]), ephemeral=True)

#=========================================
class StatusActions(discord.ui.View):
    def __init__(self,fac): 
        super().__init__(timeout=400)
        self.fac=fac

    @discord.ui.button(label="✏ EDITAR INFOS",style=discord.ButtonStyle.primary)
    async def editar_infos(self,interaction,_):
        await interaction.response.send_modal(EditarFac(self.fac))

    @discord.ui.button(label="🔄 EDITAR SEGMENTO",style=discord.ButtonStyle.secondary)
    async def editar_segmento(self,interaction,_):
        await interaction.response.send_message("Escolha o novo segmento:", view=SelectSegmentoEditar(self.fac), ephemeral=True)

    @discord.ui.button(label="🗑 DELETAR",style=discord.ButtonStyle.red)
    async def deletar(self,interaction,_):
        confirm_view = ConfirmarDelecao(self.fac)
        await interaction.response.send_message(
            f"⚠️ **Tem certeza que deseja deletar a facção '{self.fac}'?**\n"
            "Esta ação não pode ser desfeita!",
            view=confirm_view,
            ephemeral=True
        )

    @discord.ui.button(label="🔄 ATUALIZAR LÍDERES",style=discord.ButtonStyle.green)
    async def atualizar_lideres(self,interaction,_):
        """Atualiza manualmente as informações dos líderes"""
        await interaction.response.defer(ephemeral=True)
        
        for guild in bot.guilds:
            id_cargo = obter_id_cargo_por_fac(self.fac)
            if id_cargo:
                cargo = guild.get_role(id_cargo)
                if cargo:
                    membros_com_cargo = [membro for membro in guild.members if cargo in membro.roles]
                    atualizar_informacoes_lideres(self.fac, membros_com_cargo, guild)
        
        await interaction.followup.send(
            f"✅ Informações dos líderes da facção **{self.fac}** atualizadas!",
            ephemeral=True
        )

#=========================================
class ConfirmarDelecao(discord.ui.View):
    def __init__(self, fac_nome):
        super().__init__(timeout=60)
        self.fac_nome = fac_nome

    @discord.ui.button(label="✅ SIM, DELETAR", style=discord.ButtonStyle.danger)
    async def confirmar(self, interaction, button):
        deletar_fac(self.fac_nome)
        await interaction.response.edit_message(
            content=f"🗑️ Facção '{self.fac_nome}' deletada com sucesso!",
            view=None
        )

    @discord.ui.button(label="❌ NÃO, CANCELAR", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction, button):
        await interaction.response.edit_message(
            content="✅ Deleção cancelada.",
            view=None
        )

#=========================================
class SelectSegmentoEditar(discord.ui.View):
    def __init__(self, fac_nome):
        super().__init__(timeout=120)
        self.fac_nome = fac_nome
        self.select = discord.ui.Select(placeholder="Escolha o segmento",
        options=[
            discord.SelectOption(label="🔫 Armas"),
            discord.SelectOption(label="💣 Munição"),
            discord.SelectOption(label="🧪 Lavagem"),
            discord.SelectOption(label="💊 Drogas")
        ])
        self.select.callback=self.callback
        self.add_item(self.select)

    async def callback(self,interaction):
        # Carregar dados atuais
        fac_atual = carregar_fac(self.fac_nome)
        
        # Atualizar apenas o segmento, mantendo o status original
        salvar_fac(
            self.fac_nome,
            self.select.values[0],  # Novo segmento
            fac_atual["cds"],       # Mantém CDS
            fac_atual["termos"],    # Mantém termos
            fac_atual["staff"],     # Mantém staff
            fac_atual["lideres"],   # Mantém líderes
            fac_atual["status"]     # ✅ MANTÉM O STATUS ORIGINAL
        )
        
        # Enviar confirmação
        await interaction.response.send_message(
            f"✅ Segmento da facção **{self.fac_nome}** alterado para **{self.select.values[0]}**!", 
            ephemeral=True
        )

#=========================================
class EditarFac(discord.ui.Modal,title="✏ Editar Informações da FAC"):
    def __init__(self, fac_nome):
        super().__init__()
        self.fac_nome = fac_nome
        d = carregar_fac(fac_nome)

        self.nome = discord.ui.TextInput(label="Nome", default=d["nome"])
        self.cds = discord.ui.TextInput(label="CDS", default=d["cds"])
        self.termos = discord.ui.TextInput(label="Termos", default=d["termos"])
        self.staff = discord.ui.TextInput(label="Staff", default=d["staff"])
        self.lideres = discord.ui.TextInput(label="Líderes", default=d["lideres"], style=discord.TextStyle.paragraph)

        for f in (self.nome, self.cds, self.termos, self.staff, self.lideres): 
            self.add_item(f)

    async def on_submit(self,interaction):
        # Carregar dados atuais para manter o segmento e status
        fac_atual = carregar_fac(self.fac_nome)
        
        # Salvar mantendo o segmento e status originais
        salvar_fac(
            self.nome.value,
            fac_atual["segmento"],  # ✅ MANTÉM O SEGMENTO ORIGINAL
            self.cds.value,
            self.termos.value,
            self.staff.value,
            self.lideres.value,
            fac_atual["status"]     # ✅ MANTÉM O STATUS ORIGINAL
        )

        # Se mudou o nome, deletar o registro antigo
        if self.nome.value != self.fac_nome:
            deletar_fac(self.fac_nome)

        # ENVIAR PARA CANAL DE ENTREGUES (atualização) - COM STAFF E USUÁRIO FORA DO EMBED
        embed = discord.Embed(
            title=f"✏ FACÇÃO ATUALIZADA: {self.nome.value}",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="SEGMENTO", value=fac_atual["segmento"], inline=True)
        embed.add_field(name="CDS", value=self.cds.value, inline=True)
        embed.add_field(name="TERMOS", value=self.termos.value, inline=True)
        embed.add_field(name="LÍDERES", value=self.lideres.value, inline=False)
        embed.add_field(name="STATUS", value=fac_atual["status"], inline=True)  # ✅ STATUS ORIGINAL
        embed.set_footer(text=f"Atualizada em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        canal_entregues = bot.get_channel(CANAL_ENTREGUES)
        if canal_entregues:
            # Enviar mensagem com staff responsável e usuário que clicou
            mensagem_conteudo = (
                f"**👤 STAFF RESPONSÁVEL:** {self.staff.value}\n"
                f"**🎮 SOLICITADO POR:** {interaction.user.mention}"
            )
            await canal_entregues.send(content=mensagem_conteudo, embed=embed)
            print(f"✅ Facção {self.nome.value} atualizada no canal")

        await interaction.response.send_message("✔ FAC Editada!",ephemeral=True)

# COMANDOS ADICIONAIS
@bot.command(name="verificar_lideres")
@commands.has_permissions(administrator=True)
async def verificar_lideres_comando(ctx):
    """Verifica manualmente todas as facções"""
    await ctx.send("🔍 Verificando líderes de todas as facções...")
    
    for guild in bot.guilds:
        cargos_sem_lideres = await verificar_lideres_no_servidor(guild)
        
        if cargos_sem_lideres:
            embed = discord.Embed(
                title="📋 RELATÓRIO DE LÍDERES",
                description=f"**Facções sem líderes:** {len(cargos_sem_lideres)}",
                color=0xff9900,
                timestamp=discord.utils.utcnow()
            )
            
            for cargo_info in cargos_sem_lideres:
                fac_data = cargo_info["fac_data"]
                qtd_lideres = fac_data.get("qtd_lideres", 0)
                
                embed.add_field(
                    name=f"• {cargo_info['nome_fac']}",
                    value=f"**Cargo:** {cargo_info['nome_cargo']}\n"
                          f"**Líderes encontrados:** {qtd_lideres}\n"
                          f"**Status:** {fac_data['status']}",
                    inline=False
                )
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("✅ Todas as facções têm líderes ativos!")

@bot.command(name="lideres")
async def comando_lideres(ctx, *, fac_nome=None):
    """Mostra informações detalhadas dos líderes de uma facção"""
    if not fac_nome:
        # Listar todas as facções entregues
        faccoes_entregues = listar_fac_entregues()
        
        if not faccoes_entregues:
            await ctx.send("❌ Nenhuma facção entregue encontrada!")
            return
        
        embed = discord.Embed(
            title="👑 LÍDERES DAS FACÇÕES ENTREGUES",
            description="Selecione uma facção para ver detalhes dos líderes:",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        for fac_nome in faccoes_entregues[:15]:  # Limitar a 15
            fac_data = carregar_fac(fac_nome)
            qtd_lideres = int(fac_data.get("qtd_lideres", 0) or 0)  # ✅ CONVERTE
            
            embed.add_field(
                name=f"• {fac_nome}",
                value=f"**Líderes:** {qtd_lideres} ativo(s)\n"
                      f"**Status:** {fac_data['status']}",
                inline=True
            )
        
        embed.set_footer(text=f"Total: {len(faccoes_entregues)} facções entregues")
        await ctx.send(embed=embed)
    else:
        # Mostrar informações específicas de uma facção
        fac_data = carregar_fac(fac_nome)
        
        if not fac_data:
            await ctx.send(f"❌ Facção '{fac_nome}' não encontrada!")
            return
        
        if fac_data["status"] != "🟢 ENTREGUE":
            await ctx.send(f"ℹ️ A facção '{fac_nome}' não está entregue atualmente.")
            return
        
        qtd_lideres = int(fac_data.get("qtd_lideres", 0) or 0)  # ✅ CONVERTE
        nomes_lideres = fac_data.get("nomes_lideres", "Não verificado")
        
        embed = discord.Embed(
            title=f"👑 LÍDERES DA FACÇÃO: {fac_nome}",
            description=f"**Status:** {fac_data['status']}\n"
                       f"**Segmento:** {fac_data['segmento']}\n"
                       f"**Última verificação:** {fac_data.get('ultima_verificacao', 'Não verificado')}",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        if qtd_lideres > 0:
            embed.add_field(
                name=f"✅ LÍDERES ATIVOS ({qtd_lideres})",
                value=nomes_lideres,
                inline=False
            )
        else:
            embed.add_field(
                name="⚠️ SEM LÍDERES",
                value="Esta facção não possui líderes ativos no momento.",
                inline=False
            )
        
        embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        await ctx.send(embed=embed)

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    print("🚀 Iniciando bot...")
    print(f"📏 Comprimento do token: {len(TOKEN)} caracteres")
    
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ FALHA: Token inválido!")
        print("Verifique se o token está correto no SquareCloud")
    except Exception as e:
        print(f"❌ Erro: {type(e).__name__}: {e}")
