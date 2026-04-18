import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# =============================================
# CONFIGURACIÓN
# =============================================
TOKEN = os.getenv('TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

# IDs de Roles
ROLES = {
    'BOT_MANAGER':   1489015586347286689,
    'FUNDADOR':      1489015243563864144,
    'ADMINISTRADOR': 1489015430650532065,
    'MODERADOR':     1489015508278706186,
    'MIEMBRO':       1489017167348367492,
}

# Colores para los embeds (formato hexadecimal)
COLORS = {
    'RULES':  0x5865F2,
    'VERIFY': 0x57F287,
    'NEW':    0xFEE75C,
    'EVENTO': 0xEB459E,
    'ERROR':  0xED4245,
}

# =============================================
# SETUP DEL BOT
# =============================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree


# =============================================
# FUNCIÓN: Comprobar si el usuario es admin
# =============================================
def is_admin(member: discord.Member) -> bool:
    admin_role_ids = {ROLES['FUNDADOR'], ROLES['ADMINISTRADOR'], ROLES['BOT_MANAGER']}
    return (
        member.guild_permissions.administrator or
        any(r.id in admin_role_ids for r in member.roles)
    )


# =============================================
# VISTA: Botón de verificación
# =============================================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Sin timeout para que persista tras reiniciar

    @discord.ui.button(label='Verificarme 🏀', style=discord.ButtonStyle.success, custom_id='verify_button')
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        guild = interaction.guild
        role = guild.get_role(ROLES['MIEMBRO'])

        if role is None:
            await interaction.response.send_message(
                '❌ No se encontró el rol de Miembro. Contacta a un administrador.',
                ephemeral=True
            )
            return

        if role in member.roles:
            await interaction.response.send_message(
                '✅ ¡Ya tienes el rol de **🏀 Miembro**!',
                ephemeral=True
            )
            return

        try:
            await member.add_roles(role, reason='Verificación automática')
            await interaction.response.send_message(
                '🎉 ¡Verificado! Se te ha otorgado el rol **🏀 Miembro**. ¡Bienvenido al servidor!',
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                '❌ No tengo permisos para asignarte el rol. Contacta a un administrador.',
                ephemeral=True
            )


# =============================================
# EVENTO: Bot listo
# =============================================
@bot.event
async def on_ready():
    # Registrar la vista persistente del botón de verificación
    bot.add_view(VerifyView())

    # Sincronizar comandos slash con el servidor
    guild = discord.Object(id=GUILD_ID)
    tree.copy_global_to(guild=guild)
    await tree.sync(guild=guild)

    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name='🏀 Verificando miembros'
    ))
    print(f'✅ Bot conectado como: {bot.user} | Comandos sincronizados.')


# =============================================
# COMANDO: /rules
# =============================================
@tree.command(name='rules', description='📋 Muestra las reglas del servidor en este canal')
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def rules(interaction: discord.Interaction):
    if not is_admin(interaction.user):
        await interaction.response.send_message('❌ No tienes permisos para usar este comando.', ephemeral=True)
        return

    embed = discord.Embed(
        title='📋 Reglas del Servidor',
        description='> Bienvenido al servidor. Por favor, lee y respeta las siguientes reglas para mantener una comunidad sana y divertida.\n\u200b',
        color=COLORS['RULES']
    )
    embed.add_field(name='1️⃣ — Respeto mutuo',
                    value='Trata a todos con respeto. No se tolera el acoso, insultos, discriminación ni actitudes tóxicas.',
                    inline=False)
    embed.add_field(name='2️⃣ — Sin spam',
                    value='No hagas spam de mensajes, emojis, menciones o imágenes. Usa cada canal para su propósito.',
                    inline=False)
    embed.add_field(name='3️⃣ — Contenido apropiado',
                    value='No compartas contenido NSFW, violento o ilegal en ningún canal del servidor.',
                    inline=False)
    embed.add_field(name='4️⃣ — Sin publicidad',
                    value='Prohibido publicitar otros servidores, productos o servicios sin permiso previo del staff.',
                    inline=False)
    embed.add_field(name='5️⃣ — Escucha al Staff',
                    value='Las decisiones del equipo de moderación son definitivas.',
                    inline=False)
    embed.add_field(name='6️⃣ — Usa los canales correctamente',
                    value='Mantén las conversaciones en los canales correspondientes.',
                    inline=False)
    embed.add_field(name='7️⃣ — Idioma',
                    value='El idioma principal del servidor es el **español**.',
                    inline=False)
    embed.add_field(name='\u200b',
                    value='*El incumplimiento puede resultar en advertencia, silencio o expulsión.*',
                    inline=False)
    embed.set_footer(text='¡Gracias por leer las reglas! 🏀')
    embed.timestamp = discord.utils.utcnow()

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message('✅ Reglas enviadas.', ephemeral=True)


# =============================================
# COMANDO: /verify
# =============================================
@tree.command(name='verify', description='✅ Envía el mensaje de verificación con botón')
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def verify(interaction: discord.Interaction):
    if not is_admin(interaction.user):
        await interaction.response.send_message('❌ No tienes permisos para usar este comando.', ephemeral=True)
        return

    embed = discord.Embed(
        title='✅ Verificación del Servidor',
        description=(
            '¡Bienvenido al servidor! 🎉\n\n'
            'Para acceder a todos los canales y convertirte en miembro oficial, '
            'pulsa el botón de abajo.\n\n'
            '🏀 Recibirás el rol **🏀 Miembro** al verificarte.'
        ),
        color=COLORS['VERIFY']
    )
    embed.set_footer(text='Solo necesitas verificarte una vez.')
    embed.timestamp = discord.utils.utcnow()

    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message('✅ Mensaje de verificación enviado.', ephemeral=True)


# =============================================
# COMANDO: /new
# =============================================
@tree.command(name='new', description='📢 Envía un anuncio/novedad embed')
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.describe(
    titulo='Título del anuncio',
    mensaje='Contenido del anuncio',
    link='Enlace opcional (URL)'
)
async def new(interaction: discord.Interaction, titulo: str, mensaje: str, link: str = None):
    if not is_admin(interaction.user):
        await interaction.response.send_message('❌ No tienes permisos para usar este comando.', ephemeral=True)
        return

    embed = discord.Embed(
        title=f'📢 {titulo}',
        description=mensaje,
        color=COLORS['NEW']
    )
    if link:
        embed.add_field(name='🔗 Enlace', value=f'[Haz clic aquí]({link})', inline=False)

    embed.set_footer(
        text=f'Publicado por {interaction.user.display_name}',
        icon_url=interaction.user.display_avatar.url
    )
    embed.timestamp = discord.utils.utcnow()

    await interaction.channel.send(content='@everyone', embed=embed)
    await interaction.response.send_message('✅ Anuncio publicado.', ephemeral=True)


# =============================================
# COMANDO: /evento
# =============================================
@tree.command(name='evento', description='🎉 Crea un evento con reacción para apuntarse')
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.describe(
    titulo='Título del evento',
    mensaje='Descripción del evento',
    emoji='Emoji de reacción para unirse'
)
async def evento(interaction: discord.Interaction, titulo: str, mensaje: str, emoji: str):
    if not is_admin(interaction.user):
        await interaction.response.send_message('❌ No tienes permisos para usar este comando.', ephemeral=True)
        return

    embed = discord.Embed(
        title=f'🎉 Evento: {titulo}',
        description=mensaje,
        color=COLORS['EVENTO']
    )
    embed.add_field(
        name='\u200b',
        value=f'Reacciona con **{emoji}** para apuntarte al evento.',
        inline=False
    )
    embed.set_footer(
        text=f'Evento creado por {interaction.user.display_name}',
        icon_url=interaction.user.display_avatar.url
    )
    embed.timestamp = discord.utils.utcnow()

    await interaction.response.send_message('✅ Evento creado.', ephemeral=True)
    msg = await interaction.channel.send(content='@everyone', embed=embed)

    try:
        await msg.add_reaction(emoji)
    except discord.HTTPException:
        await interaction.channel.send(
            f'⚠️ No se pudo añadir la reacción **{emoji}** automáticamente. Añádela manualmente.'
        )


# =============================================
# INICIAR BOT
# =============================================
bot.run(TOKEN)
