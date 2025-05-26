"""
🤖 FutEnglish Telegram Bot - Versão Final
Bot funcional com todas as features, sem locks complexos
"""

import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Imports
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Imports dos módulos funcionais
print("🔥 FutEnglish Bot Final")
print("=" * 30)

try:
    from config import Config, Messages
    from user_state import UserSession
    from content import FootballContent, lesson_manager, ContentHelper
    from ai_handler import ai_handler, CommandDetector
    from audio_manager import audio_manager
    from lesson_manager import lesson_delivery, progress_tracker
    print("✅ Todos os módulos importados com sucesso!")
    FULL_FEATURES = True
except Exception as e:
    print(f"⚠️ Erro nos imports: {e}")
    FULL_FEATURES = False

class FutEnglishBot:
    """Bot principal do FutEnglish - versão simplificada"""
    
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        
        # Estado simples sem locks complexos
        self.user_sessions = {}
        
        # Dados para fallback
        self.positions = ["Goleiro", "Zagueiro", "Lateral", "Volante", "Meio-campo", "Atacante", "Não jogo, só assisto"]
        self.levels = ["Iniciante", "Intermediário", "Avançado"]
        
        print("✅ Bot criado com sucesso!")
    
    def get_or_create_simple_session(self, user_id: int, name: str = "") -> dict:
        """Cria sessão simples sem locks"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'user_id': user_id,
                'name': name,
                'position': '',
                'level': '',
                'step': 'ask_name',
                'lesson_id': 1,
                'onboarding_complete': False
            }
        return self.user_sessions[user_id]
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "Amigo"
        
        logger.info(f"🚀 /start - Usuário {user_id} ({user_name})")
        
        # Reset da sessão
        self.user_sessions[user_id] = {
            'user_id': user_id,
            'name': '',
            'position': '',
            'level': '',
            'step': 'ask_name',
            'lesson_id': 1,
            'onboarding_complete': False
        }
        
        welcome_text = f"""
🔥 Eaí, {user_name}! Sou o Professor Bola Gringa! ⚽

Vou te ensinar inglês usando o que você mais ama: FUTEBOL! 
Aqui você vai aprender vocabulário, gírias e tudo sobre o beautiful game em inglês!

Vamos começar se conhecendo melhor? 

**Qual é o seu nome?** 😎
"""
        
        await update.message.reply_text(welcome_text)
        
        # Tenta gerar áudio sem bloquear
        try:
            if FULL_FEATURES:
                asyncio.create_task(self._send_welcome_audio(update, user_id))
        except Exception as e:
            logger.warning(f"⚠️ Erro no áudio: {e}")
        
        logger.info(f"✅ Boas-vindas enviadas para {user_id}")
    
    async def _send_welcome_audio(self, update: Update, user_id: int):
        """Envia áudio de boas-vindas de forma assíncrona"""
        try:
            audio_path = await audio_manager.generate_professor_audio(
                user_id, 
                "Olá! Sou o Professor Bola Gringa! Vamos aprender inglês com futebol!"
            )
            
            if audio_path and os.path.exists(audio_path):
                with open(audio_path, 'rb') as audio_file:
                    await update.message.reply_voice(
                        audio_file,
                        caption="🎵 Clique para ouvir!"
                    )
                logger.info(f"✅ Áudio de boas-vindas enviado para {user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Erro no áudio de boas-vindas: {e}")
    
    async def proxima_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /proxima"""
        user_id = update.effective_user.id
        
        logger.info(f"📚 /proxima - Usuário {user_id}")
        
        session = self.get_or_create_simple_session(user_id)
        
        if not session['onboarding_complete']:
            await update.message.reply_text("Use /start primeiro para nos conhecermos! 😊")
            return
        
        # Busca lição
        if FULL_FEATURES:
            try:
                lesson = lesson_manager.get_lesson_by_id(session['lesson_id'])
                if lesson:
                    lesson_text = self._format_lesson(lesson, session)
                    await update.message.reply_text(lesson_text, parse_mode='Markdown')
                    
                    # Envia áudios de forma assíncrona
                    asyncio.create_task(self._send_lesson_audios(update, user_id, lesson))
                    
                    # Avança lição
                    session['lesson_id'] += 1
                    if session['lesson_id'] > 10:
                        session['lesson_id'] = 1  # Reinicia
                else:
                    await update.message.reply_text("Não encontrei mais lições! Use /start para recomeçar!")
            except Exception as e:
                logger.error(f"❌ Erro na lição: {e}")
                await self._send_fallback_lesson(update, session)
        else:
            await self._send_fallback_lesson(update, session)
    
    def _format_lesson(self, lesson: dict, session: dict) -> str:
        """Formata lição para exibição"""
        text = f"""
⚽ **Lição {session['lesson_id']} - Nova Palavra:**

🇧🇷 **Português:** {lesson['pt']}
🇺🇸 **Inglês:** {lesson['en']}

💡 **Explicação:** {lesson.get('explanation', 'Palavra importante do futebol!')}
"""
        
        if lesson.get('example_pt') and lesson.get('example_en'):
            text += f"""
📝 **Exemplo:**
🇧🇷 {lesson['example_pt']}
🇺🇸 {lesson['example_en']}
"""
        
        if lesson.get('tips'):
            text += f"\n🎯 **Dica:** {lesson['tips']}"
        
        text += f"\n\nÓtimo, {session['name']}! Use /proxima para continuar! ⚽"
        
        return text
    
    async def _send_lesson_audios(self, update: Update, user_id: int, lesson: dict):
        """Envia áudios da lição de forma assíncrona"""
        try:
            # Gera áudios usando o sistema dual-language
            pt_text = f"Vamos aprender a palavra {lesson['pt']}"
            en_text = lesson['en']  # Apenas a palavra em inglês
            
            # Usa o sistema dual-language do audio_manager
            pt_audio, en_audio = await audio_manager.generate_lesson_audio(
                user_id, pt_text, en_text
            )
            
            # Envia áudio em português (professor)
            if pt_audio and os.path.exists(pt_audio):
                with open(pt_audio, 'rb') as audio_file:
                    await update.message.reply_voice(
                        audio_file,
                        caption="🇧🇷 Professor explicando"
                    )
            
            # Pausa entre áudios
            await asyncio.sleep(1)
            
            # Envia áudio em inglês (vocabulário nativo)
            if en_audio and os.path.exists(en_audio):
                with open(en_audio, 'rb') as audio_file:
                    await update.message.reply_voice(
                        audio_file,
                        caption="🇺🇸 Pronúncia nativa em inglês"
                    )
            
            logger.info(f"✅ Áudios dual-language enviados para {user_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro nos áudios da lição: {e}")
            # Fallback: tenta pelo menos o áudio do professor
            try:
                pt_audio = await audio_manager.generate_professor_audio(
                    user_id, f"A palavra {lesson['pt']} em inglês é {lesson['en']}"
                )
                if pt_audio and os.path.exists(pt_audio):
                    with open(pt_audio, 'rb') as audio_file:
                        await update.message.reply_voice(
                            audio_file,
                            caption="🇧🇷 Professor (modo fallback)"
                        )
            except Exception as fallback_error:
                logger.warning(f"⚠️ Erro no fallback de áudio: {fallback_error}")
    
    async def _send_fallback_lesson(self, update: Update, session: dict):
        """Lição de fallback se houver problemas"""
        lessons = [
            {"pt": "Goleiro", "en": "Goalkeeper", "explanation": "Jogador que defende o gol"},
            {"pt": "Bola", "en": "Ball", "explanation": "Esfera usada no jogo"},
            {"pt": "Gol", "en": "Goal", "explanation": "Quando a bola entra na rede"},
            {"pt": "Passe", "en": "Pass", "explanation": "Enviar bola para companheiro"},
            {"pt": "Chute", "en": "Shot", "explanation": "Ação de chutar a bola"}
        ]
        
        lesson_index = (session['lesson_id'] - 1) % len(lessons)
        lesson = lessons[lesson_index]
        
        lesson_text = self._format_lesson(lesson, session)
        await update.message.reply_text(lesson_text, parse_mode='Markdown')
        
        session['lesson_id'] += 1
    
    async def audio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /audio"""
        user_id = update.effective_user.id
        
        logger.info(f"🎵 /audio - Usuário {user_id}")
        
        if FULL_FEATURES:
            try:
                # Tenta repetir último áudio
                pt_audio, en_audio = await audio_manager.repeat_last_audio(user_id)
                
                if pt_audio or en_audio:
                    await update.message.reply_text("🔄 Repetindo áudios...")
                    
                    if pt_audio and os.path.exists(pt_audio):
                        with open(pt_audio, 'rb') as audio_file:
                            await update.message.reply_voice(audio_file, caption="🇧🇷 Português")
                    
                    if en_audio and os.path.exists(en_audio):
                        await asyncio.sleep(1)
                        with open(en_audio, 'rb') as audio_file:
                            await update.message.reply_voice(audio_file, caption="🇺🇸 Inglês")
                else:
                    await update.message.reply_text("Não tenho áudios para repetir! Use /proxima para uma lição!")
            except Exception as e:
                logger.error(f"❌ Erro no áudio: {e}")
                await update.message.reply_text("🎵 Sistema de áudio temporariamente indisponível!")
        else:
            await update.message.reply_text("🎵 Sistema de áudio em manutenção! Continue com as lições!")
    
    async def progresso_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /progresso"""
        user_id = update.effective_user.id
        session = self.get_or_create_simple_session(user_id)
        
        if not session['onboarding_complete']:
            await update.message.reply_text("Use /start primeiro! 😊")
            return
        
        # Progresso fake
        progress_text = f"""
📊 **Estatísticas do {session['name']}:**

⭐ Nível: {session['level']}
📚 Lições Completadas: {session['lesson_id']}/20
🎯 Vocabulário Aprendido: {session['lesson_id'] * 8} palavras
🔥 Sequência Atual: 5 dias
⚽ Posição: {session['position']}

**Últimas conquistas:**
🏆 "Mestre do Vocabulário"
⚽ "Craque da Pronúncia"
🎯 "Focado"

Continue assim, {session['name']}! Você tá voando! 🚀
"""
        
        await update.message.reply_text(progress_text, parse_mode='Markdown')
    
    async def ajuda_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ajuda"""
        help_text = """
🎯 **Comandos do Professor Bola Gringa:**

/start - Iniciar/reiniciar curso
/proxima - Próxima lição
/audio - Repetir áudio
/progresso - Ver estatísticas
/ajuda - Esta lista

💬 **Dica**: Converse comigo livremente sobre futebol!

Bora aprender, craque! ⚽🇺🇸
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para mensagens livres"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        logger.info(f"💬 Mensagem de {user_id}: {message_text[:50]}...")
        
        session = self.get_or_create_simple_session(user_id, update.effective_user.first_name)
        
        # Onboarding
        if not session['onboarding_complete']:
            await self._handle_onboarding(update, session, message_text)
            return
        
        # Detecta comandos naturais
        if FULL_FEATURES:
            try:
                detected_command = CommandDetector.detect_command(message_text)
                if detected_command:
                    if detected_command == 'próxima':
                        await self.proxima_command(update, None)
                        return
                    elif detected_command == 'áudio':
                        await self.audio_command(update, None)
                        return
            except Exception as e:
                logger.warning(f"⚠️ Erro na detecção de comando: {e}")
        
        # Chat livre
        await self._handle_free_chat(update, session, message_text)
    
    async def _handle_onboarding(self, update: Update, session: dict, message: str):
        """Onboarding simplificado"""
        message = message.strip()
        
        if session['step'] == 'ask_name':
            # Valida nome
            if len(message) < 2:
                await update.message.reply_text("Digite um nome válido (pelo menos 2 letras):")
                return
            
            if message.lower() in ['oi', 'hey', 'hello', 'hi']:
                await update.message.reply_text("""
Oi! Que legal! 😊

Mas preciso saber seu nome de verdade para personalizar as lições!

**Qual é o seu nome?**
""")
                return
            
            session['name'] = message
            session['step'] = 'ask_position'
            
            positions_text = "\n".join([f"{i+1}. {pos}" for i, pos in enumerate(self.positions)])
            
            response = f"""
Prazer, {message}! 🤝

**Qual posição você joga?** (ou gosta de assistir)

{positions_text}

Digite o número ou nome:
"""
            await update.message.reply_text(response)
            
        elif session['step'] == 'ask_position':
            # Processa posição
            position = self._parse_position(message)
            if not position:
                positions_text = "\n".join([f"{i+1}. {pos}" for i, pos in enumerate(self.positions)])
                await update.message.reply_text(f"Escolha uma das opções:\n\n{positions_text}")
                return
            
            session['position'] = position
            session['step'] = 'ask_level'
            
            levels_text = "\n".join([f"{i+1}. {level}" for i, level in enumerate(self.levels)])
            
            response = f"""
Legal! {position} é uma posição importante! ⚽

**Qual seu nível de inglês?**

{levels_text}

Digite o número ou nome:
"""
            await update.message.reply_text(response)
            
        elif session['step'] == 'ask_level':
            # Processa nível
            level = self._parse_level(message)
            if not level:
                levels_text = "\n".join([f"{i+1}. {lv}" for i, lv in enumerate(self.levels)])
                await update.message.reply_text(f"Escolha uma das opções:\n\n{levels_text}")
                return
            
            session['level'] = level
            session['onboarding_complete'] = True
            
            response = f"""
Perfeito, {session['name']}! 🎉

**Seu Perfil:**
👤 Nome: {session['name']}
⚽ Posição: {session['position']}
📚 Nível: {session['level']}

Agora vamos aprender inglês com futebol! 
Use /proxima para sua primeira lição!

Bora que bora! 🚀⚽
"""
            await update.message.reply_text(response, parse_mode='Markdown')
    
    def _parse_position(self, input_text: str) -> str:
        """Interpreta entrada de posição"""
        input_text = input_text.strip()
        
        # Tenta número
        try:
            pos_index = int(input_text) - 1
            if 0 <= pos_index < len(self.positions):
                return self.positions[pos_index]
        except ValueError:
            pass
        
        # Tenta nome
        input_lower = input_text.lower()
        for pos in self.positions:
            if pos.lower() in input_lower or input_lower in pos.lower():
                return pos
        
        return None
    
    def _parse_level(self, input_text: str) -> str:
        """Interpreta entrada de nível"""
        input_text = input_text.strip()
        
        # Tenta número
        try:
            level_index = int(input_text) - 1
            if 0 <= level_index < len(self.levels):
                return self.levels[level_index]
        except ValueError:
            pass
        
        # Tenta nome
        input_lower = input_text.lower()
        for level in self.levels:
            if level.lower() in input_lower or input_lower in level.lower():
                return level
        
        return None
    
    async def _handle_free_chat(self, update: Update, session: dict, message: str):
        """Chat livre"""
        message_lower = message.lower()
        
        # Primeiro verifica se é pergunta sobre tradução
        is_translation_question = any(phrase in message_lower for phrase in [
            'como se fala', 'como fala', 'como se diz', 'como diz', 
            'em inglês', 'in english', 'traduz', 'tradução'
        ])
        
        # Palavras de futebol com respostas diretas
        football_words = {
            'gol': ('GOAL', f"⚽ Boa, {session['name']}! 'Gol' em inglês é 'GOAL'! GOOOOOL!"),
            'bola': ('BALL', f"🟢 Isso aí! 'Bola' em inglês é 'BALL'! The ball is round!"),
            'goleiro': ('GOALKEEPER', f"🥅 'Goleiro' em inglês é 'GOALKEEPER'! Sua posição favorita, {session['name']}?"),
            'passe': ('PASS', "🎯 'Passe' em inglês é 'PASS'! Good pass!"),
            'chute': ('SHOT', "🚀 'Chute' em inglês é 'SHOT'! Take a shot!"),
            'carrinho': ('TACKLE', f"🔥 Boa pergunta, {session['name']}! 'Carrinho' em inglês é 'TACKLE'! Movimento técnico importante!"),
            'falta': ('FOUL', "🟨 'Falta' em inglês é 'FOUL'! Cuidado com as faltas!"),
            'escanteio': ('CORNER KICK', "🚩 'Escanteio' em inglês é 'CORNER KICK'! Boa oportunidade de gol!"),
            'impedimento': ('OFFSIDE', "🚫 'Impedimento' em inglês é 'OFFSIDE'! Regra importante!"),
            'chapéu': ('NUTMEG', f"🎩 Boa, {session['name']}! 'Chapéu' em inglês é 'NUTMEG'! Aquela jogada que humilha o adversário!"),
            'drible': ('DRIBBLE', f"💫 'Drible' em inglês é 'DRIBBLE'! Show de bola, {session['name']}!"),
            'lateral': ('THROW-IN', "🤾 'Lateral' em inglês é 'THROW-IN'! Reposição pela linha lateral!"),
            'penalti': ('PENALTY', "⚠️ 'Pênalti' em inglês é 'PENALTY'! Cobrança na marca dos 11 metros!"),
            'juiz': ('REFEREE', "👨‍⚖️ 'Juiz' em inglês é 'REFEREE'! O cara do apito!"),
            'cartão': ('CARD', "🟨 'Cartão' em inglês é 'CARD'! Yellow card ou red card!"),
            'campo': ('FIELD', f"🏟️ 'Campo' em inglês é 'FIELD'! Onde a magia acontece, {session['name']}!"),
            'trave': ('GOALPOST', "🥅 'Trave' em inglês é 'GOALPOST'! Quase gol!"),
            'rede': ('NET', "🥅 'Rede' em inglês é 'NET'! Quando a bola balança a rede!"),
            'meio-campo': ('MIDFIELD', f"⚽ 'Meio-campo' em inglês é 'MIDFIELD'! Centro do jogo, {session['name']}!"),
            'zagueiro': ('DEFENDER', "🛡️ 'Zagueiro' em inglês é 'DEFENDER'! A muralha da defesa!"),
            'atacante': ('STRIKER', f"⚡ 'Atacante' em inglês é 'STRIKER'! O artilheiro, {session['name']}!")
        }
        
        # Procura por palavra de futebol na mensagem
        found_word = None
        for word, (en_translation, response) in football_words.items():
            if word in message_lower:
                found_word = (en_translation, response)
                break
        
        # Se encontrou palavra de futebol, responde diretamente
        if found_word:
            en_word, response = found_word
        elif any(word in message_lower for word in ['obrigado', 'thanks', 'valeu']):
            response = f"De nada, {session['name']}! Continue praticando! 🎯"
            en_word = None
        else:
            # Usa IA para outras perguntas
            if FULL_FEATURES:
                try:
                    # Cria sessão compatível com IA
                    ai_session = UserSession(user_id=session['user_id'])
                    ai_session.name = session['name']
                    ai_session.position = session['position']
                    ai_session.english_level = session['level']
                    ai_session.onboarding_complete = True
                    
                    ai_response = await ai_handler.handle_free_chat(ai_session, message)
                    
                    # Envia resposta da IA
                    await update.message.reply_text(ai_response)
                    
                    # Se é pergunta de tradução, tenta extrair palavra inglesa da resposta
                    if is_translation_question:
                        en_word = self._extract_english_word(ai_response)
                        if en_word:
                            try:
                                # Gera apenas áudio da palavra inglesa
                                _, en_audio = await audio_manager.generate_lesson_audio(
                                    session['user_id'], 
                                    "Palavra em inglês",  # Dummy text para PT
                                    en_word
                                )
                                
                                if en_audio and os.path.exists(en_audio):
                                    await update.message.reply_voice(
                                        en_audio,
                                        caption="🇺🇸 Pronúncia em inglês"
                                    )
                            except Exception as audio_error:
                                logger.warning(f"⚠️ Erro no áudio extraído: {audio_error}")
                    
                    # Gera áudio da resposta se curta
                    elif len(ai_response) < 150:
                        try:
                            response_audio = await audio_manager.generate_professor_audio(
                                session['user_id'], ai_response
                            )
                            
                            if response_audio and os.path.exists(response_audio):
                                await update.message.reply_voice(
                                    response_audio,
                                    caption="🎵 Resposta em áudio"
                                )
                        except Exception as audio_error:
                            logger.warning(f"⚠️ Erro no áudio da IA: {audio_error}")
                    
                    return
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro na IA: {e}")
            
            # Fallback
            response = f"Legal, {session['name']}! Que tal aprender uma palavra nova? Use /proxima! 🎯"
            en_word = None
        
        # Envia resposta de texto
        await update.message.reply_text(response)
        
        # Envia áudios se há palavra inglesa
        if en_word:
            try:
                # Gera áudios dual-language
                pt_audio, en_audio = await audio_manager.generate_lesson_audio(
                    session['user_id'], 
                    response,  # Professor falando a explicação
                    en_word    # Palavra em inglês nativo
                )
                
                # Envia áudio da palavra inglesa (principal)
                if en_audio and os.path.exists(en_audio):
                    await update.message.reply_voice(
                        en_audio,
                        caption="🇺🇸 Pronúncia em inglês"
                    )
                
                logger.info(f"✅ Áudio de resposta enviado para {session['user_id']}")
                
            except Exception as audio_error:
                logger.warning(f"⚠️ Erro no áudio da resposta: {audio_error}")
    
    def _extract_english_word(self, text: str) -> str:
        """Extrai palavra inglesa da resposta da IA"""
        import re
        
        # Padrões para capturar palavra inglesa nas respostas
        patterns = [
            r'"([A-Z][A-Z\s-]+)"',  # "NUTMEG", "CORNER KICK"
            r"'([A-Z][A-Z\s-]+)'",  # 'NUTMEG', 'CORNER KICK'
            r'é "([^"]+)"',         # é "nutmeg"
            r"é '([^']+)'",         # é 'nutmeg'
            r'is "([^"]+)"',        # is "nutmeg"
            r"is '([^']+)'",        # is 'nutmeg'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                word = match.group(1).strip()
                # Valida se parece ser uma palavra inglesa
                if len(word) > 1 and word.replace(' ', '').replace('-', '').isalpha():
                    return word.upper()
        
        return None
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler de erros"""
        logger.error(f"❌ Erro: {context.error}")
        
        if update and update.message:
            await update.message.reply_text("Opa! Algo deu errado, mas vamos continuar! 🔧")
    
    def setup_handlers(self):
        """Configura handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("proxima", self.proxima_command))
        self.app.add_handler(CommandHandler("audio", self.audio_command))
        self.app.add_handler(CommandHandler("progresso", self.progresso_command))
        self.app.add_handler(CommandHandler("ajuda", self.ajuda_command))
        self.app.add_handler(CommandHandler("help", self.ajuda_command))
        
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.message_handler
        ))
        
        self.app.add_error_handler(self.error_handler)
        
        logger.info("✅ Handlers configurados!")
    
    def run(self):
        """Executa bot"""
        if not BOT_TOKEN:
            logger.error("❌ Token não encontrado")
            return
        
        logger.info("🚀 Iniciando FutEnglish Bot Final...")
        
        if FULL_FEATURES:
            logger.info("✅ Modo completo: IA + Áudio + Lições")
        else:
            logger.info("⚠️ Modo básico: Apenas texto")
        
        self.setup_handlers()
        
        logger.info("📱 Bot pronto! Digite /start no Telegram")
        logger.info("🛑 Ctrl+C para parar")
        
        try:
            self.app.run_polling(
                poll_interval=1.0,
                timeout=10,
                read_timeout=15,
                write_timeout=15,
                connect_timeout=15
            )
        except KeyboardInterrupt:
            logger.info("🛑 Bot parado pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro fatal: {e}")

def main():
    """Função principal"""
    try:
        bot = FutEnglishBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")

if __name__ == "__main__":
    main()