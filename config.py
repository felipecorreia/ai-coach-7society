"""
⚙️ FutEnglish Configuration Manager
Gerencia todas as configurações, APIs e constantes do bot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações centralizadas do bot"""
    
    # ============================================
    # 🤖 TELEGRAM BOT SETTINGS
    # ============================================
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Configurações do bot
    BOT_USERNAME = 'futenglish_professor_bot'  # Ajuste conforme seu bot
    BOT_NAME = 'Professor Bola Gringa'
    
    # Timeout e rate limiting
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
    RATE_LIMIT_MESSAGES = 10  # mensagens por minuto
    RATE_LIMIT_WINDOW = 60   # janela em segundos
    
    # ============================================
    # 🧠 GOOGLE GEMINI SETTINGS
    # ============================================
    GENAI_API_KEY = os.getenv('GENAI_API_KEY')
    GEMINI_MODEL = 'gemini-2.0-flash'
    
    # Configurações de geração
    GEMINI_CONFIG = {
        'temperature': 0.7,
        'top_p': 0.8,
        'top_k': 40,
        'max_output_tokens': 1000
    }
    
    # ============================================
    # 🎵 GOOGLE CLOUD TTS SETTINGS
    # ============================================
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Configurações de voz - Professor (Português)
    TTS_PT_CONFIG = {
        'language_code': 'pt-BR',
        'name': 'pt-BR-Wavenet-B',  # Voz masculina
        'ssml_gender': 'MALE',
        'speaking_rate': 0.9,
        'pitch': 0.0,
        'volume_gain_db': 0.0
    }
    
    # Configurações de voz - Vocabulário (Inglês)
    TTS_EN_CONFIG = {
        'language_code': 'en-US', 
        'name': 'en-US-Wavenet-D',  # Voz masculina
        'ssml_gender': 'MALE',
        'speaking_rate': 0.85,  # Mais lento para aprendizado
        'pitch': 0.0,
        'volume_gain_db': 0.0
    }
    
    # Configurações de áudio
    AUDIO_CONFIG = {
        'audio_encoding': 'OGG_OPUS',  # Formato nativo Telegram
        'sample_rate_hertz': 48000,
        'effects_profile_id': ['telephony-class-application']
    }
    
    # ============================================
    # 📁 DIRETÓRIOS E ARQUIVOS
    # ============================================
    BASE_DIR = Path(__file__).parent
    TEMP_AUDIO_DIR = Path(os.getenv('TEMP_AUDIO_DIR', './temp_audio'))
    
    # Criar diretórios se não existirem
    TEMP_AUDIO_DIR.mkdir(exist_ok=True)
    
    # ============================================
    # 🎯 BOT BEHAVIOR SETTINGS
    # ============================================
    
    # Debug e logging
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    VERBOSE_LOGGING = os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'
    
    # Mensagens do sistema
    MAX_MESSAGE_LENGTH = 4000  # Limite Telegram
    DEFAULT_LANGUAGE = 'pt-BR'
    
    # Timeouts para áudio
    AUDIO_GENERATION_TIMEOUT = 30
    AUDIO_CLEANUP_INTERVAL = 3600  # 1 hora
    
    # ============================================
    # 🎮 COMANDOS DO BOT
    # ============================================
    COMMANDS = {
        'start': 'Iniciar/reiniciar curso',
        'próxima': 'Próxima lição',
        'audio': 'Repetir áudio atual', 
        'ajuda': 'Lista de comandos',
        'progresso': 'Ver estatísticas fake'
    }
    
    # Aliases para comandos (aceitar variações)
    COMMAND_ALIASES = {
        'proxima': 'próxima',
        'proximo': 'próxima',
        'next': 'próxima',
        'áudio': 'audio',
        'som': 'audio',
        'repeat': 'audio',
        'help': 'ajuda',
        'comandos': 'ajuda',
        'progress': 'progresso',
        'stats': 'progresso'
    }

class Messages:
    """Mensagens padrão do bot"""
    
    # ============================================
    # 🎯 MENSAGENS DE SISTEMA
    # ============================================
    
    WELCOME = """
🔥 Eaí, futuro craque! Sou o Professor Bola Gringa! ⚽

Vou te ensinar inglês usando o que você mais ama: FUTEBOL! 
Aqui você vai aprender vocabulário, gírias e tudo sobre o beautiful game em inglês!

Vamos começar se conhecendo melhor? 😎
"""
    
    ERROR_GENERIC = """
⚠️ Opa! Deu algum problema aqui...
Tenta de novo, parceiro! Se continuar, me chama que a gente resolve! 🔧
"""
    
    ERROR_AUDIO = """
🎵 Problema no áudio, meu amigo!
Mas não se preocupa, vou te responder só por texto mesmo! 📝
"""
    
    RATE_LIMIT = """
⏰ Calma aí, craque! 
Você tá enviando muitas mensagens muito rápido!
Respira fundo e tenta de novo em alguns segundos! 😅
"""
    
    # ============================================
    # 🎮 MENSAGENS DE COMANDOS
    # ============================================
    
    HELP = """
🎯 **Comandos do Professor Bola Gringa:**

/start - Começar do zero
/próxima - Próxima lição
/áudio - Repetir último áudio  
/progresso - Ver suas estatísticas
/ajuda - Esta lista

💬 **Dica**: Você também pode conversar comigo livremente sobre futebol em inglês!

Bora aprender, craque! ⚽🇺🇸
"""
    
    PROGRESS_FAKE = """
📊 **Suas Estatísticas (Demo):**

⭐ Nível: Intermediário Avançado
📚 Lições Completadas: 15/20
🎯 Vocabulário Aprendido: 127 palavras
🔥 Sequência Atual: 8 dias
⚽ Posição: {position}

**Últimas conquistas:**
🏆 "Mestre do Vocabulário" - 100+ palavras
⚽ "Craque da Pronúncia" - 50+ áudios
🎯 "Focado" - 7 dias seguidos

Continue assim, {name}! Você tá voando! 🚀
"""

class Prompts:
    """Prompts para o AI Handler"""
    
    PROFESSOR_SYSTEM = """
Você é o Professor Bola Gringa, especialista em ensinar inglês através do futebol para brasileiros.

REGRAS IMPORTANTES:
- FALE APENAS EM PORTUGUÊS na sua resposta
- NUNCA pronuncie palavras em inglês 
- Se mencionar palavra inglesa, diga "essa palavra em inglês" ou "em inglês isso é"
- Seja animado, positivo e encorajador
- Use referências do futebol brasileiro e internacional
- Máximo 3 frases por resposta
- Conecte com a posição do jogador quando relevante
- Use emojis de futebol moderadamente

CONTEXTO DO USUÁRIO:
- Nome: {name}
- Posição: {position} 
- Nível: {level}
- Lição Atual: {current_lesson}

Se a pergunta não for sobre futebol, redirecione gentilmente para o tema mantendo a persona.
"""
    
    LESSON_CONTEXT = """
CONTEXTO DA LIÇÃO ATUAL:
Palavra PT: {pt_word}
Palavra EN: {en_word}
Explicação: {explanation}

Responda de forma educativa sobre esta palavra no contexto do futebol.
"""

def validate_config():
    """Valida se todas as configurações necessárias estão presentes"""
    required_vars = [
        ('TELEGRAM_BOT_TOKEN', Config.TELEGRAM_BOT_TOKEN),
        ('GENAI_API_KEY', Config.GENAI_API_KEY)
    ]
    
    missing = []
    for var_name, var_value in required_vars:
        if not var_value:
            missing.append(var_name)
    
    if missing:
        raise ValueError(f"Variáveis de ambiente obrigatórias não configuradas: {', '.join(missing)}")
    
    return True

# Validar configurações ao importar
if __name__ != '__main__':
    validate_config()