from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackContext
import os
from dotenv import load_dotenv

load_dotenv("../.env")
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
EMAIL = os.getenv("INSTAGRAM_EMAIL")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Defina os estados
START, WAITING_FOR_INPUT, PAUSED = range(3)

# Variável global para gerenciar o estado de pausa
is_paused = False

async def start(update: Update, context: CallbackContext) -> int:
    global is_paused
    is_paused = False
    await update.message.reply_text(
        "Olá! Envie uma mensagem para iniciar a conversa. Use /pause para pausar e /resume para retomar. Digite 'cancelar' a qualquer momento para sair."
    )
    return WAITING_FOR_INPUT

async def handle_input(update: Update, context: CallbackContext) -> int:
    global is_paused
    
    if is_paused:
        await update.message.reply_text("O bot está pausado. Use /resume para retomar.")
        return WAITING_FOR_INPUT

    user_input = update.message.text.lower()
    if user_input == 'cancelar':
        await update.message.reply_text("Conversa cancelada.")
        return ConversationHandler.END

    # Processa o input do usuário
    await update.message.reply_text(f"Você disse: {user_input}")
    return WAITING_FOR_INPUT

async def pause(update: Update, context: CallbackContext) -> int:
    global is_paused
    is_paused = True
    await update.message.reply_text("O bot está agora pausado. Use /resume para retomar.")
    return WAITING_FOR_INPUT

async def resume(update: Update, context: CallbackContext) -> int:
    global is_paused
    is_paused = False
    await update.message.reply_text("O bot foi retomado. Envie uma mensagem para continuar.")
    return WAITING_FOR_INPUT

async def cancel(update: Update, context: CallbackContext) -> int:
    global is_paused
    is_paused = False
    await update.message.reply_text("Conversa cancelada.")
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token(TOKEN_TELEGRAM).build()

    # Defina o ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)
            ],
            PAUSED: [
                CommandHandler('resume', resume)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Adicione o ConversationHandler ao dispatcher
    application.add_handler(conv_handler)
    
    # Adicione comandos de pausa e retomada como handlers separados
    application.add_handler(CommandHandler('pause', pause))
    application.add_handler(CommandHandler('resume', resume))

    print("Bot está iniciando...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()