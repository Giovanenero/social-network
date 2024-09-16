from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import os

from model.youtube import YouTube
from model.instagram import Instagram

TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")

async def posts_extraction(update: Update, context: CallbackContext) -> int:
    instagram = Instagram(update)
    result = await instagram.login()
    if result is not None:
        await update.message.reply_text("Iniciando a extração de publicações do Instagram...")
        await instagram.extract_posts()
        await update.message.reply_text("Extração concluída!")
    else:
        await update.message.reply_text("Erro: Não foi possível fazer login!")
    return

async def profiles_extraction(update: Update, context: CallbackContext) -> int:
    instagram = Instagram(update)
    result = await instagram.login()
    if result is not None:
        await update.message.reply_text("Iniciando a extração de perfils do Instagram...")
        await instagram.extract_profiles()
        await update.message.reply_text("Extração concluída!")
    else:
        await update.message.reply_text("Erro: Não foi possível fazer login!")

async def statistics_extraction(update: Update, context: CallbackContext) -> int:
    instagram = Instagram(update)
    instagram.extract_statistics()
    await update.message.reply_text("Registro de estatísticas de perfil e publicações do Instagram realizado com sucesso!")

async def youtube_extraction(update: Update, context: CallbackContext) -> int:
    youtube = YouTube(update)

    await update.message.reply_text("Iniciando a extração do canal do Youtube...")
    youtube.extract_channel()
    await update.message.reply_text("Extração concluída!")

    await update.message.reply_text("Iniciando a extração de playlists do canal do Youtube...")
    youtube.extract_playlists()
    await update.message.reply_text("Extração concluída!")

    await update.message.reply_text("Iniciando a extração de videos do canal do Youtube...")
    youtube.extract_videos()
    await update.message.reply_text("Extração concluída!")

    await update.message.reply_text("Iniciando a extração de comentários e respostas de vídeos do canal do Youtube...")
    youtube.extract_comments()
    await update.message.reply_text("Extração concluída!")

async def comments_extraction(update: Update, context: CallbackContext) -> int:
    instagram = Instagram(update)
    result = await instagram.login()
    if result is not None:
        await update.message.reply_text("Iniciando a extração de comentários e respostas de comentários do Instagram...")
        await instagram.extract_comments()
        await update.message.reply_text("Extração concluída!")
    else:
        await update.message.reply_text("Erro: Não foi possível fazer login!")
    
def main() -> None:
    application = Application.builder().token(TOKEN_TELEGRAM).build()

    application.add_handler(CommandHandler("posts", posts_extraction))
    application.add_handler(CommandHandler("profiles", profiles_extraction))
    application.add_handler(CommandHandler("youtube", youtube_extraction))
    application.add_handler(CommandHandler("statistics", statistics_extraction))
    application.add_handler(CommandHandler("comments", comments_extraction))
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, continue_extraction))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()