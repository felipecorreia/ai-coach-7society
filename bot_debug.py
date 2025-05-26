"""
🔍 FutEnglish Debug Bot
Versão simplificada para diagnóstico de problemas
"""

import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuração básica
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carrega token
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

print("🔍 DIAGNÓSTICO INICIADO")
print(f"Token existe: {bool(BOT_TOKEN)}")
print(f"Token válido: {BOT_TOKEN[:10] if BOT_TOKEN else 'NONE'}...{BOT_TOKEN[-10:] if BOT_TOKEN else ''}")

class DebugBot:
    def __init__(self):
        print("🔧 Criando aplicação...")
        try:
            self.app = Application.builder().token(BOT_TOKEN).build()
            print("✅ Aplicação criada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao criar aplicação: {e}")
            raise
        
        self.user_data = {}
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start simplificado"""
        user_id = update.effective_user.id
        name = update.effective_user.first_name or "Amigo"
        
        print(f"🚀 /start recebido de {user_id} ({name})")
        logger.info(f"🚀 /start recebido de {user_id} ({name})")
        
        try:
            message = f"Oi {name}! Bot funcionando! Digite qualquer coisa para testar."
            await update.message.reply_text(message)
            
            print(f"✅ Resposta enviada para {user_id}")
            logger.info(f"✅ Resposta enviada para {user_id}")
            
        except Exception as e:
            print(f"❌ Erro ao responder: {e}")
            logger.error(f"❌ Erro ao responder: {e}")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler de mensagens simples"""
        user_id = update.effective_user.id
        message = update.message.text
        
        print(f"💬 Mensagem de {user_id}: {message}")
        logger.info(f"💬 Mensagem de {user_id}: {message}")
        
        try:
            response = f"Recebi: '{message}' - Bot está funcionando!"
            await update.message.reply_text(response)
            
            print(f"✅ Eco enviado para {user_id}")
            logger.info(f"✅ Eco enviado para {user_id}")
            
        except Exception as e:
            print(f"❌ Erro no eco: {e}")
            logger.error(f"❌ Erro no eco: {e}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler de erros"""
        print(f"❌ ERRO: {context.error}")
        logger.error(f"❌ ERRO: {context.error}")
    
    def setup(self):
        """Configura handlers"""
        print("🔧 Configurando handlers...")
        
        try:
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
            self.app.add_error_handler(self.error_handler)
            
            print("✅ Handlers configurados!")
            
        except Exception as e:
            print(f"❌ Erro ao configurar handlers: {e}")
            raise
    
    def run(self):
        """Executa bot"""
        print("🚀 Iniciando bot debug...")
        
        if not BOT_TOKEN:
            print("❌ Token não encontrado!")
            return
        
        try:
            self.setup()
            
            print("📱 Bot pronto! Digite /start no Telegram")
            print("🛑 Ctrl+C para parar")
            print("=" * 50)
            
            # Executa polling
            self.app.run_polling(
                poll_interval=1.0,
                timeout=10,
                read_timeout=15,
                write_timeout=15,
                connect_timeout=15
            )
            
        except KeyboardInterrupt:
            print("🛑 Bot parado pelo usuário")
        except Exception as e:
            print(f"❌ Erro fatal: {e}")
            logger.error(f"❌ Erro fatal: {e}")

def main():
    """Função principal de debug"""
    print("🔍 FutEnglish Debug Bot")
    print("=" * 30)
    
    try:
        bot = DebugBot()
        bot.run()
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        logger.error(f"❌ Erro na inicialização: {e}")

if __name__ == "__main__":
    main()