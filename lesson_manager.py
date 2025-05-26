"""
📚 FutEnglish Lesson Manager
Sistema de lições educacionais e progressão
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import random

from user_state import UserSession, user_state_manager
from audio_manager import audio_manager

logger = logging.getLogger(__name__)

class LessonDelivery:
    """Gerencia entrega e apresentação de lições"""
    
    def __init__(self):
        from content import lesson_manager as content_lesson_manager, ContentHelper
        self.content_manager = content_lesson_manager
        self.content_helper = ContentHelper()
    
    async def start_lesson(self, session: UserSession) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Inicia uma nova lição
        
        Args:
            session: Sessão do usuário
            
        Returns:
            Tupla (texto_resposta, caminho_audio_pt, caminho_audio_en)
        """
        logger.info(f"📚 Iniciando lição para usuário {session.user_id}")
        
        # Busca lição atual
        lesson = self.content_manager.get_lesson_by_id(session.current_lesson_id)
        
        if not lesson:
            # Se não encontrou, pega lição aleatória baseada no nível
            lesson = self.content_manager.get_random_lesson(session.english_level)
            if lesson:
                user_state_manager.update_session(session.user_id, current_lesson_id=lesson['id'])
        
        if not lesson:
            return "Opa! Não encontrei nenhuma lição disponível. Vamos conversar sobre futebol!", None, None
        
        # Gera texto da lição
        lesson_text = self._format_lesson_text(lesson, session)
        
        # Gera áudios
        pt_audio, en_audio = await self._generate_lesson_audio(session, lesson)
        
        logger.info(f"✅ Lição {lesson['id']} entregue para usuário {session.user_id}")
        
        return lesson_text, pt_audio, en_audio
    
    async def next_lesson(self, session: UserSession) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Avança para próxima lição
        
        Args:
            session: Sessão do usuário
            
        Returns:
            Tupla (texto_resposta, caminho_audio_pt, caminho_audio_en)
        """
        logger.info(f"📚 Avançando para próxima lição - usuário {session.user_id}")
        
        # Marca lição atual como completa (fake)
        if session.current_lesson_id not in session.lessons_completed:
            session.lessons_completed.append(session.current_lesson_id)
        
        # Busca próxima lição
        next_lesson = self.content_manager.get_next_lesson(
            session.current_lesson_id, 
            session.english_level
        )
        
        if not next_lesson:
            return "Parabéns! Você completou todas as lições disponíveis! 🎉", None, None
        
        # Atualiza sessão
        user_state_manager.update_session(
            session.user_id, 
            current_lesson_id=next_lesson['id']
        )
        
        # Gera resposta de transição
        transition_text = self._generate_transition_text(session, next_lesson)
        
        # Gera áudios
        pt_audio, en_audio = await self._generate_lesson_audio(session, next_lesson)
        
        return transition_text, pt_audio, en_audio
    
    def _format_lesson_text(self, lesson: Dict[str, Any], session: UserSession) -> str:
        """Formata texto da lição para exibição"""
        text = f"⚽ **Lição {lesson['id']} - {lesson.get('category', 'Vocabulário').title()}**\n\n"
        
        # Saudação personalizada
        greetings = [
            f"Opa, {session.name}! Vamos aprender uma palavra importante!",
            f"E aí, {session.name}! Bora para mais uma palavra de futebol!",
            f"Beleza, {session.name}! Hoje temos uma palavra massa!",
            f"Fala, {session.name}! Preparado para mais vocabulário?"
        ]
        text += random.choice(greetings) + "\n\n"
        
        # Palavra principal
        text += f"🇧🇷 **Português:** {lesson['pt']}\n"
        text += f"🇺🇸 **Inglês:** {lesson['en']}\n"
        
        if lesson.get('pronunciation'):
            text += f"🗣️ **Pronúncia:** {lesson['pronunciation']}\n"
        
        # Explicação
        if lesson.get('explanation'):
            text += f"\n💡 **O que é:** {lesson['explanation']}\n"
        
        # Exemplo
        if lesson.get('example_pt') and lesson.get('example_en'):
            text += f"\n📝 **Exemplo:**\n"
            text += f"🇧🇷 {lesson['example_pt']}\n"
            text += f"🇺🇸 {lesson['example_en']}\n"
        
        # Dica
        if lesson.get('tips'):
            text += f"\n🎯 **Dica:** {lesson['tips']}\n"
        
        # Conexão com posição do jogador
        if session.position and session.position != "Não jogo, só assisto":
            position_tip = self._get_position_specific_tip(lesson, session.position)
            if position_tip:
                text += f"\n⚽ **Para {session.position}:** {position_tip}"
        
        text += "\n\n📱 Use /próxima para continuar ou /áudio para ouvir novamente!"
        
        return text
    
    def _generate_transition_text(self, session: UserSession, next_lesson: Dict[str, Any]) -> str:
        """Gera texto de transição entre lições"""
        transitions = [
            f"Muito bem, {session.name}! Vamos para a próxima! 🚀",
            f"Boa, {session.name}! Agora vem outra palavra importante! ⚽",
            f"Excelente! Bora continuar aprendendo, {session.name}! 💪",
            f"Mandou bem! Próxima palavra chegando, {session.name}! 🔥"
        ]
        
        transition = random.choice(transitions)
        lesson_text = self._format_lesson_text(next_lesson, session)
        
        return f"{transition}\n\n{lesson_text}"
    
    async def _generate_lesson_audio(self, session: UserSession, lesson: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """Gera áudios para a lição"""
        try:
            # Texto para áudio em português (professor)
            pt_text = f"Vamos aprender a palavra {lesson['pt']}"
            
            # Texto para áudio em inglês (vocabulário)
            en_text = lesson['en']
            
            # Gera áudios
            pt_audio, en_audio = await audio_manager.generate_lesson_audio(
                session.user_id, pt_text, en_text
            )
            
            return pt_audio, en_audio
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar áudio da lição: {e}")
            return None, None
    
    def _get_position_specific_tip(self, lesson: Dict[str, Any], position: str) -> Optional[str]:
        """Retorna dica específica para a posição do jogador"""
        word = lesson['pt'].lower()
        
        position_tips = {
            "Goleiro": {
                "goleiro": "Essa é sua posição! Em inglês, você é o 'goalkeeper'!",
                "defesa": "Muito importante para você! 'Save' é quando você defende!",
                "bola": "A 'ball' que você mais precisa pegar!",
                "gol": "O 'goal' que você precisa defender!"
            },
            "Zagueiro": {
                "zagueiro": "Sua posição! 'Defender' ou 'center-back' no inglês!",
                "defesa": "Seu trabalho principal! 'Defense' é fundamental!",
                "passe": "Muito importante para iniciar jogadas! 'Pass' certeiro!",
                "cabeceada": "Arma poderosa na defesa e no ataque!"
            },
            "Atacante": {
                "atacante": "Sua posição! 'Striker' ou 'forward' em inglês!",
                "gol": "Seu objetivo principal! 'Goal' é sua especialidade!",
                "chute": "'Shot' certeiro é sua marca registrada!",
                "driblar": "Sua arma secreta! 'Dribble' com estilo!"
            },
            "Meio-campo": {
                "meio-campo": "Sua posição! 'Midfielder' é você!",
                "passe": "Sua especialidade! 'Pass' é sua ferramenta principal!",
                "assistência": "'Assist' é o que você faz de melhor!",
                "visão de jogo": "Sua qualidade principal no campo!"
            }
        }
        
        return position_tips.get(position, {}).get(word)

class ProgressTracker:
    """Rastreador de progresso educacional (com dados fake)"""
    
    def __init__(self):
        self.fake_data_generator = FakeProgressGenerator()
    
    def get_user_progress(self, session: UserSession) -> str:
        """Retorna progresso do usuário (dados fake)"""
        return self.fake_data_generator.generate_progress_report(session)
    
    def get_lesson_stats(self, user_id: int) -> Dict[str, Any]:
        """Retorna estatísticas da lição atual"""
        session = user_state_manager.get_session(user_id)
        if not session:
            return {}
        
        current_lesson = content_manager.get_lesson_by_id(session.current_lesson_id)
        
        return {
            'current_lesson_id': session.current_lesson_id,
            'current_lesson': current_lesson.get('pt', '') if current_lesson else '',
            'lessons_completed': len(session.lessons_completed),
            'total_interactions': session.total_interactions,
            'session_duration': str(session.get_session_duration()),
            'english_level': session.english_level
        }

class FakeProgressGenerator:
    """Gerador de dados fake para demonstração"""
    
    def generate_progress_report(self, session: UserSession) -> str:
        """Gera relatório de progresso fake"""
        
        # Dados aleatórios mas consistentes para cada usuário
        seed = hash(session.user_id) % 1000
        random.seed(seed)
        
        # Estatísticas fake
        lessons_completed = random.randint(8, 18)
        total_lessons = 20
        vocabulary_learned = random.randint(85, 150)
        daily_streak = random.randint(3, 21)
        accuracy = random.randint(75, 95)
        
        # Conquistas fake
        achievements = [
            "🏆 Primeiro Gol", "⚽ Craque da Pronúncia", "🎯 Focado",
            "🔥 Sequência de Ouro", "📚 Estudioso", "🌟 All Star",
            "💪 Persistente", "🎮 Interativo", "👑 Mestre das Palavras"
        ]
        
        user_achievements = random.sample(achievements, random.randint(2, 5))
        
        # Progresso por categoria
        categories_progress = {
            "Posições": random.randint(70, 100),
            "Ações": random.randint(60, 95),
            "Equipamentos": random.randint(80, 100),
            "Campo": random.randint(65, 90),
            "Táticas": random.randint(40, 80)
        }
        
        report = f"""
📊 **Estatísticas do {session.name}**

⭐ **Progresso Geral:**
📚 Lições: {lessons_completed}/{total_lessons} ({int(lessons_completed/total_lessons*100)}%)
🎯 Vocabulário: {vocabulary_learned} palavras aprendidas
🔥 Sequência: {daily_streak} dias consecutivos
🎯 Precisão: {accuracy}%
⚽ Posição: {session.position}

📈 **Progresso por Categoria:**
"""
        
        for category, progress in categories_progress.items():
            bar = "█" * int(progress/10) + "░" * (10 - int(progress/10))
            report += f"{category}: {bar} {progress}%\n"
        
        report += f"\n🏆 **Conquistas Desbloqueadas:**\n"
        for achievement in user_achievements:
            report += f"{achievement}\n"
        
        report += f"\n💡 **Dica:** Continue praticando para desbloquear mais conquistas!"
        report += f"\n🚀 **Continue assim, {session.name}! Você está indo muito bem!**"
        
        return report

class LessonContent:
    """Gerenciador de conteúdo das lições"""
    
    @staticmethod
    def get_lesson_by_category(category: str, level: str) -> Optional[Dict[str, Any]]:
        """Busca lição por categoria"""
        from content import lesson_manager as content_manager
        lessons = content_manager.get_lessons_by_level(level)
        
        category_lessons = [l for l in lessons if l.get('category') == category]
        
        if category_lessons:
            return random.choice(category_lessons)
        
        return None
    
    @staticmethod
    def search_lessons(query: str, level: str) -> list:
        """Busca lições por palavra-chave"""
        from content import lesson_manager as content_manager
        lessons = content_manager.get_lessons_by_level(level)
        
        query_lower = query.lower()
        matches = []
        
        for lesson in lessons:
            if (query_lower in lesson.get('pt', '').lower() or 
                query_lower in lesson.get('en', '').lower() or
                query_lower in lesson.get('explanation', '').lower()):
                matches.append(lesson)
        
        return matches

# Instância global
lesson_delivery = LessonDelivery()
progress_tracker = ProgressTracker()