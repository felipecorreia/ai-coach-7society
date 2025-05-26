"""
🤖 FutEnglish AI Handler
Integração com Google Gemini para conversação inteligente
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from config import Config, Prompts
from user_state import UserSession

logger = logging.getLogger(__name__)

class GeminiClient:
    """Cliente para Google Gemini AI"""
    
    def __init__(self):
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa cliente Gemini"""
        try:
            genai.configure(api_key=Config.GENAI_API_KEY)
            self.model = genai.GenerativeModel(
                Config.GEMINI_MODEL,
                generation_config=genai.GenerationConfig(**Config.GEMINI_CONFIG)
            )
            logger.info("✅ Google Gemini client inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Gemini: {e}")
            self.model = None
    
    async def generate_response(self, prompt: str) -> Optional[str]:
        """
        Gera resposta usando Gemini
        
        Args:
            prompt: Prompt completo para o modelo
            
        Returns:
            Resposta gerada ou None em caso de erro
        """
        if not self.model:
            logger.error("Modelo Gemini não inicializado")
            return None
        
        try:
            logger.info("🤖 Gerando resposta com Gemini...")
            
            # Executa geração em executor para não bloquear
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            if response and response.text:
                logger.info("✅ Resposta gerada com sucesso")
                return response.text.strip()
            else:
                logger.warning("⚠️ Resposta vazia do Gemini")
                return None
                
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"❌ Erro Google Gemini API: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro inesperado no Gemini: {e}")
            return None

class ConversationManager:
    """Gerencia contexto e histórico de conversação"""
    
    def __init__(self):
        self.conversation_history: Dict[int, list] = {}
        self.max_history_length = 10  # Últimas 10 interações
    
    def add_interaction(self, user_id: int, user_message: str, ai_response: str):
        """Adiciona interação ao histórico"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'timestamp': datetime.now(),
            'user': user_message,
            'ai': ai_response
        })
        
        # Mantém apenas últimas interações
        if len(self.conversation_history[user_id]) > self.max_history_length:
            self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history_length:]
    
    def get_context_summary(self, user_id: int) -> str:
        """Retorna resumo do contexto da conversa"""
        if user_id not in self.conversation_history:
            return ""
        
        recent_interactions = self.conversation_history[user_id][-3:]  # Últimas 3
        
        if not recent_interactions:
            return ""
        
        context = "CONTEXTO DA CONVERSA RECENTE:\n"
        for i, interaction in enumerate(recent_interactions, 1):
            context += f"Interação {i}:\n"
            context += f"Usuário: {interaction['user'][:100]}...\n"
            context += f"Professor: {interaction['ai'][:100]}...\n\n"
        
        return context
    
    def clear_history(self, user_id: int):
        """Limpa histórico do usuário"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]

class PromptBuilder:
    """Construtor de prompts contextuais"""
    
    @staticmethod
    def build_system_prompt(session: UserSession) -> str:
        """Constrói prompt base do sistema"""
        return Prompts.PROFESSOR_SYSTEM.format(
            name=session.name or "Amigo",
            position=session.position or "Jogador",
            level=session.english_level or "Intermediário",
            current_lesson=session.current_lesson_id
        )
    
    @staticmethod
    def build_lesson_prompt(session: UserSession, user_message: str) -> str:
        """Constrói prompt para contexto de lição"""
        from content import lesson_manager as content_lesson_manager
        
        # Busca lição atual
        current_lesson = content_lesson_manager.get_lesson_by_id(session.current_lesson_id)
        
        system_prompt = PromptBuilder.build_system_prompt(session)
        
        if current_lesson:
            lesson_context = Prompts.LESSON_CONTEXT.format(
                pt_word=current_lesson.get('pt', ''),
                en_word=current_lesson.get('en', ''),
                explanation=current_lesson.get('explanation', '')
            )
            system_prompt += "\n\n" + lesson_context
        
        full_prompt = f"{system_prompt}\n\nMENSAGEM DO USUÁRIO: {user_message}"
        return full_prompt
    
    @staticmethod
    def build_free_chat_prompt(session: UserSession, user_message: str, context: str = "") -> str:
        """Constrói prompt para chat livre"""
        system_prompt = PromptBuilder.build_system_prompt(session)
        
        if context:
            system_prompt += f"\n\n{context}"
        
        full_prompt = f"{system_prompt}\n\nMENSAGEM DO USUÁRIO: {user_message}"
        return full_prompt

class ResponseFilter:
    """Filtro para respostas da IA"""
    
    @staticmethod
    def filter_response(response: str) -> str:
        """Aplica filtros na resposta da IA"""
        if not response:
            return ""
        
        # Remove possíveis palavras inglesas que escaparam
        filtered = ResponseFilter._replace_english_words(response)
        
        # Limita tamanho
        if len(filtered) > Config.MAX_MESSAGE_LENGTH:
            filtered = filtered[:Config.MAX_MESSAGE_LENGTH-50] + "..."
        
        # Remove quebras de linha excessivas
        import re
        filtered = re.sub(r'\n{3,}', '\n\n', filtered)
        
        return filtered.strip()
    
    @staticmethod
    def _replace_english_words(text: str) -> str:
        """Substitui palavras inglesas comuns por equivalentes em português"""
        replacements = {
            r'\bgoal\b': 'gol',
            r'\bpass\b': 'passe', 
            r'\bshot\b': 'chute',
            r'\bball\b': 'bola',
            r'\bfield\b': 'campo',
            r'\bgoalkeeper\b': 'goleiro',
            r'\bdefender\b': 'zagueiro',
            r'\bstriker\b': 'atacante',
            r'\bmidfielder\b': 'meio-campo'
        }
        
        import re
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text

class AIHandler:
    """Handler principal para integração com IA"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.conversation_manager = ConversationManager()
        self.fallback_responses = self._load_fallback_responses()
    
    async def handle_lesson_interaction(self, session: UserSession, user_message: str) -> str:
        """
        Processa interação durante uma lição
        
        Args:
            session: Sessão do usuário
            user_message: Mensagem do usuário
            
        Returns:
            Resposta contextual da IA
        """
        logger.info(f"🤖 Processando interação de lição para usuário {session.user_id}")
        
        # Constrói prompt contextual
        prompt = PromptBuilder.build_lesson_prompt(session, user_message)
        
        # Gera resposta
        response = await self.gemini_client.generate_response(prompt)
        
        if not response:
            response = self._get_fallback_response("lesson_error")
        
        # Aplica filtros
        filtered_response = ResponseFilter.filter_response(response)
        
        # Adiciona ao histórico
        self.conversation_manager.add_interaction(
            session.user_id, user_message, filtered_response
        )
        
        return filtered_response
    
    async def handle_free_chat(self, session: UserSession, user_message: str) -> str:
        """
        Processa chat livre sobre futebol
        
        Args:
            session: Sessão do usuário
            user_message: Mensagem do usuário
            
        Returns:
            Resposta contextual da IA
        """
        logger.info(f"🤖 Processando chat livre para usuário {session.user_id}")
        
        # Obtém contexto da conversa
        context = self.conversation_manager.get_context_summary(session.user_id)
        
        # Constrói prompt
        prompt = PromptBuilder.build_free_chat_prompt(session, user_message, context)
        
        # Gera resposta
        response = await self.gemini_client.generate_response(prompt)
        
        if not response:
            response = self._get_fallback_response("chat_error")
        
        # Aplica filtros
        filtered_response = ResponseFilter.filter_response(response)
        
        # Adiciona ao histórico
        self.conversation_manager.add_interaction(
            session.user_id, user_message, filtered_response
        )
        
        return filtered_response
    
    async def explain_lesson_word(self, session: UserSession, word_id: int) -> str:
        """
        Explica palavra específica da lição
        
        Args:
            session: Sessão do usuário
            word_id: ID da palavra/lição
            
        Returns:
            Explicação detalhada
        """
        from content import lesson_manager as content_lesson_manager
        
        lesson = content_lesson_manager.get_lesson_by_id(word_id)
        
        if not lesson:
            return "Desculpa, não encontrei essa palavra! Tenta outra pergunta."
        
        explanation_prompt = f"""
{PromptBuilder.build_system_prompt(session)}

TAREFA ESPECÍFICA: Explique detalhadamente a palavra/conceito abaixo no contexto do futebol.

PALAVRA PT: {lesson['pt']}
PALAVRA EN: {lesson['en']} 
EXPLICAÇÃO BASE: {lesson.get('explanation', '')}
EXEMPLO PT: {lesson.get('example_pt', '')}
EXEMPLO EN: {lesson.get('example_en', '')}

Dê uma explicação rica e interessante, com exemplos práticos do futebol brasileiro.
"""
        
        response = await self.gemini_client.generate_response(explanation_prompt)
        
        if not response:
            return f"A palavra {lesson['pt']} em inglês é {lesson['en']}. {lesson.get('explanation', '')}"
        
        return ResponseFilter.filter_response(response)
    
    def _load_fallback_responses(self) -> Dict[str, list]:
        """Carrega respostas de fallback para quando a IA falha"""
        return {
            "lesson_error": [
                "Opa! Deu uma travada aqui, mas vamos continuar! Que tal tentar /próxima para ir para próxima lição?",
                "Eita! Probleminha técnico, mas tô aqui firme! Bora continuar aprendendo?",
                "Calma aí que já volto! Enquanto isso, quer ver seu /progresso?"
            ],
            "chat_error": [
                "Rapaz, deu um branco aqui! Mas fala aí sobre futebol que eu te respondo!",
                "Opa! Travei legal agora! Conta pra mim: qual seu time do coração?",
                "Eita! Deu ruim no sistema! Mas bora falar de futebol mesmo assim!"
            ],
            "general_error": [
                "Caramba! Algo deu errado aqui! Tenta de novo, parceiro!",
                "Opa! Probleminha técnico! Mas não desiste não, bora continuar!",
                "Eita! Deu pau aqui! Mas já já tô funcionando 100% de novo!"
            ]
        }
    
    def _get_fallback_response(self, error_type: str) -> str:
        """Retorna resposta aleatória de fallback"""
        import random
        responses = self.fallback_responses.get(error_type, self.fallback_responses["general_error"])
        return random.choice(responses)
    
    def clear_conversation_history(self, user_id: int):
        """Limpa histórico de conversa do usuário"""
        self.conversation_manager.clear_history(user_id)
    
    def get_ai_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de IA"""
        return {
            'gemini_available': self.gemini_client.model is not None,
            'active_conversations': len(self.conversation_manager.conversation_history),
            'total_interactions': sum(
                len(history) for history in self.conversation_manager.conversation_history.values()
            )
        }

class CommandDetector:
    """Detecta comandos em linguagem natural"""
    
    COMMAND_PATTERNS = {
        'próxima': [
            'próxima', 'proximo', 'próximo', 'next', 'continuar', 'avançar',
            'próxima lição', 'próxima palavra', 'vamos continuar'
        ],
        'áudio': [
            'áudio', 'audio', 'som', 'repetir', 'repeat', 'escutar',
            'repetir áudio', 'tocar de novo', 'quero ouvir'
        ],
        'progresso': [
            'progresso', 'progress', 'estatísticas', 'stats', 'como estou',
            'meu progresso', 'minhas estatísticas'
        ],
        'ajuda': [
            'ajuda', 'help', 'comandos', 'o que posso fazer',
            'como funciona', 'manual'
        ]
    }
    
    @classmethod
    def detect_command(cls, message: str) -> Optional[str]:
        """
        Detecta comando na mensagem
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            Nome do comando detectado ou None
        """
        message_lower = message.lower().strip()
        
        for command, patterns in cls.COMMAND_PATTERNS.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return command
        
        return None
    
    @classmethod
    def is_command_like(cls, message: str) -> bool:
        """Verifica se mensagem parece comando"""
        message_lower = message.lower().strip()
        
        # Mensagens muito curtas são mais prováveis de serem comandos
        if len(message_lower) <= 15:
            return cls.detect_command(message) is not None
        
        return False

# Instância global
ai_handler = AIHandler()