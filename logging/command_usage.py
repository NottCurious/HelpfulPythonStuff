from discord.ext import commands
from datetime import datetime
import convert_logging as cl

log = cl.get_logging()

async def record_usage(self, ctx: commands.Context) -> None:
    """Records Usage of Slash Commands

    Args:
        ctx (commands.Context): Message Context
    """
    log.info(
        f"{ctx.author.name} used slash command -> {ctx.command} at {ctx.message.created_at} in {ctx.guild}"
    )


async def finish_usage(self, ctx: commands.Context) -> None:
    """Records Finish Usage of Commands

    Args:
        ctx (commands.Context): Message Context
    """
    log.info(f"{ctx.author} finished using slash command: {ctx.command} in {ctx.guild}")
