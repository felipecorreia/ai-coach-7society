"""
📚 FutEnglish Content Database
Base de conhecimento com vocabulário e lições de futebol
"""

from typing import Dict, List, Any
import random

class FootballContent:
    """Base de dados do vocabulário de futebol"""
    
    # ============================================
    # ⚽ STEP 1 - VOCABULÁRIO BÁSICO
    # ============================================
    
    VOCABULARY_BASIC = [
        {
            "id": 1,
            "pt": "Goleiro",
            "en": "Goalkeeper", 
            "pronunciation": "GOAL-kee-per",
            "category": "positions",
            "explanation": "O jogador que defende o gol e pode usar as mãos dentro da área",
            "example_pt": "O goleiro fez uma defesa incrível",
            "example_en": "The goalkeeper made an incredible save",
            "tips": "Também pode ser chamado de 'keeper' ou 'goalie'"
        },
        {
            "id": 2,
            "pt": "Zagueiro",
            "en": "Defender",
            "pronunciation": "dih-FEN-der", 
            "category": "positions",
            "explanation": "Jogador que atua na defesa para proteger o gol",
            "example_pt": "O zagueiro cortou o ataque adversário",
            "example_en": "The defender stopped the opponent's attack",
            "tips": "Pode ser 'center-back' (zagueiro central) ou 'full-back' (lateral)"
        },
        {
            "id": 3,
            "pt": "Atacante", 
            "en": "Striker",
            "pronunciation": "STRAI-ker",
            "category": "positions",
            "explanation": "Jogador responsável por marcar gols",
            "example_pt": "O atacante balançou as redes",
            "example_en": "The striker scored a goal",
            "tips": "Também chamado de 'forward' ou 'center-forward'"
        },
        {
            "id": 4,
            "pt": "Meio-campo",
            "en": "Midfielder", 
            "pronunciation": "MID-feel-der",
            "category": "positions",
            "explanation": "Jogador que atua entre a defesa e o ataque",
            "example_pt": "O meio-campo distribuiu bem o jogo",
            "example_en": "The midfielder distributed the ball well",
            "tips": "Pode ser defensivo, central ou ofensivo"
        },
        {
            "id": 5,
            "pt": "Bola",
            "en": "Ball",
            "pronunciation": "BAWL",
            "category": "equipment", 
            "explanation": "A esfera usada para jogar futebol",
            "example_pt": "A bola saiu pela linha de fundo",
            "example_en": "The ball went out over the goal line",
            "tips": "Sempre use 'the ball', nunca apenas 'ball'"
        },
        {
            "id": 6,
            "pt": "Gol",
            "en": "Goal",
            "pronunciation": "GOHL",
            "category": "actions",
            "explanation": "Quando a bola entra completamente no gol adversário",
            "example_pt": "Foi um gol de placa!",
            "example_en": "It was a spectacular goal!",
            "tips": "Pode ser usado para o ato de marcar ou a estrutura física"
        },
        {
            "id": 7,
            "pt": "Passe",
            "en": "Pass",
            "pronunciation": "PAAS",
            "category": "actions",
            "explanation": "Ação de enviar a bola para um companheiro",
            "example_pt": "Que passe espetacular!",
            "example_en": "What a spectacular pass!",
            "tips": "Pode ser 'short pass' (passe curto) ou 'long pass' (passe longo)"
        },
        {
            "id": 8,
            "pt": "Chute",
            "en": "Shot",
            "pronunciation": "SHAHT",
            "category": "actions",
            "explanation": "Ação de chutar a bola em direção ao gol",
            "example_pt": "O chute foi para fora",
            "example_en": "The shot went wide",
            "tips": "Também pode ser 'kick' para chute em geral"
        },
        {
            "id": 9,
            "pt": "Campo",
            "en": "Field",
            "pronunciation": "FEELD", 
            "category": "field",
            "explanation": "O terreno onde se joga futebol",
            "example_pt": "O campo estava molhado",
            "example_en": "The field was wet",
            "tips": "Também chamado de 'pitch' no inglês britânico"
        },
        {
            "id": 10,
            "pt": "Árbitro",
            "en": "Referee",
            "pronunciation": "REF-uh-ree",
            "category": "officials",
            "explanation": "O responsável por aplicar as regras do jogo",
            "example_pt": "O árbitro marcou pênalti",
            "example_en": "The referee awarded a penalty",
            "tips": "Informalmente chamado de 'ref'"
        }
    ]
    
    # ============================================
    # 📝 STEP 2 - FRASES EM CONTEXTO  
    # ============================================
    
    VOCABULARY_PHRASES = [
        {
            "id": 11,
            "pt": "O goleiro fez uma defesa",
            "en": "The goalkeeper made a save",
            "category": "game_actions",
            "context": "Quando o goleiro impede um gol",
            "alternative": "The keeper stopped the shot"
        },
        {
            "id": 12, 
            "pt": "O atacante marcou um gol",
            "en": "The striker scored a goal",
            "category": "game_actions",
            "context": "Quando um jogador marca",
            "alternative": "The forward found the net"
        },
        {
            "id": 13,
            "pt": "Foi um passe perfeito",
            "en": "It was a perfect pass", 
            "category": "game_actions",
            "context": "Elogiando um passe bem executado",
            "alternative": "That was an excellent pass"
        },
        {
            "id": 14,
            "pt": "A bola bateu na trave",
            "en": "The ball hit the post",
            "category": "game_events", 
            "context": "Quando a bola acerta a trave",
            "alternative": "The shot struck the goalpost"
        },
        {
            "id": 15,
            "pt": "O time está atacando",
            "en": "The team is attacking",
            "category": "game_tactics",
            "context": "Descrevendo ação ofensiva",
            "alternative": "The team is on the attack"
        }
    ]
    
    # ============================================
    # 🎯 CATEGORIAS E FILTROS
    # ============================================
    
    CATEGORIES = {
        "positions": "Posições",
        "equipment": "Equipamentos", 
        "actions": "Ações",
        "field": "Campo",
        "officials": "Arbitragem",
        "game_actions": "Ações de Jogo",
        "game_events": "Eventos",
        "game_tactics": "Táticas"
    }
    
    DIFFICULTY_LEVELS = {
        "Iniciante": {"step": 1, "max_lesson": 5},
        "Intermediário": {"step": 1, "max_lesson": 10}, 
        "Avançado": {"step": 2, "max_lesson": 15}
    }
    
    # ============================================
    # 🎲 DADOS FAKE PARA DEMONSTRAÇÃO
    # ============================================
    
    FAKE_PROGRESS_DATA = {
        "total_lessons": 20,
        "vocabulary_learned": [95, 127, 156, 89, 234],  # Números aleatórios
        "daily_streak": [3, 8, 15, 2, 23],
        "achievements": [
            "🏆 Mestre do Vocabulário",
            "⚽ Craque da Pronúncia", 
            "🎯 Focado",
            "🔥 Sequência de Ouro",
            "📚 Estudioso",
            "🌟 Primeira Liga"
        ]
    }

class LessonManager:
    """Gerenciador de lições e progressão"""
    
    def __init__(self):
        self.content = FootballContent()
    
    def get_lesson_by_id(self, lesson_id: int) -> Dict[str, Any]:
        """Retorna lição específica por ID"""
        all_content = self.content.VOCABULARY_BASIC + self.content.VOCABULARY_PHRASES
        
        for item in all_content:
            if item["id"] == lesson_id:
                return item
        
        return None
    
    def get_lessons_by_level(self, level: str) -> List[Dict[str, Any]]:
        """Retorna lições apropriadas para o nível"""
        config = self.content.DIFFICULTY_LEVELS.get(level, {"step": 1, "max_lesson": 5})
        
        if config["step"] == 1:
            return self.content.VOCABULARY_BASIC[:config["max_lesson"]]
        else:
            basic = self.content.VOCABULARY_BASIC
            phrases = self.content.VOCABULARY_PHRASES[:config["max_lesson"] - len(basic)]
            return basic + phrases
    
    def get_random_lesson(self, level: str = "Intermediário") -> Dict[str, Any]:
        """Retorna lição aleatória baseada no nível"""
        lessons = self.get_lessons_by_level(level)
        return random.choice(lessons) if lessons else None
    
    def get_next_lesson(self, current_id: int, level: str) -> Dict[str, Any]:
        """Retorna próxima lição baseada na atual"""
        lessons = self.get_lessons_by_level(level)
        
        current_index = None
        for i, lesson in enumerate(lessons):
            if lesson["id"] == current_id:
                current_index = i
                break
        
        if current_index is not None and current_index + 1 < len(lessons):
            return lessons[current_index + 1]
        
        # Se chegou ao fim, volta para primeira ou lição aleatória
        return lessons[0] if lessons else self.get_random_lesson(level)
    
    def get_fake_progress(self, name: str, position: str) -> str:
        """Gera dados fake de progresso para demonstração"""
        data = self.content.FAKE_PROGRESS_DATA
        
        # Seleciona valores aleatórios dos arrays
        vocab_count = random.choice(data["vocabulary_learned"])
        streak = random.choice(data["daily_streak"])
        achievements = random.sample(data["achievements"], 3)
        
        progress_text = f"""
📊 **Estatísticas do {name}:**

⭐ Nível: Intermediário Avançado  
📚 Lições Completadas: 15/{data["total_lessons"]}
🎯 Vocabulário Aprendido: {vocab_count} palavras
🔥 Sequência Atual: {streak} dias
⚽ Posição Favorita: {position}

**Últimas conquistas:**
"""
        
        for achievement in achievements:
            progress_text += f"{achievement}\n"
        
        progress_text += f"\nContinue assim, {name}! Você tá voando! 🚀"
        
        return progress_text

class ContentHelper:
    """Helpers para manipulação de conteúdo"""
    
    @staticmethod
    def clean_text_for_tts(text: str) -> str:
        """Limpa texto para TTS (remove emojis, markdown, etc)"""
        import re
        
        # Remove emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        text = emoji_pattern.sub(r'', text)
        
        # Remove markdown
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # *italic*
        text = re.sub(r'`(.*?)`', r'\1', text)        # `code`
        
        # Remove pontuação excessiva
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '.', text)
        
        # Limpa espaços
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    @staticmethod
    def extract_english_words(text: str) -> List[str]:
        """Extrai palavras em inglês do texto para áudio separado"""
        import re
        
        # Padrões para identificar palavras inglesas
        english_patterns = [
            r'\b[A-Za-z]+(?:\s[A-Za-z]+)*\b'  # Palavras básicas
        ]
        
        english_words = []
        for pattern in english_patterns:
            matches = re.findall(pattern, text)
            english_words.extend(matches)
        
        return list(set(english_words))  # Remove duplicatas
    
    @staticmethod
    def format_lesson_text(lesson: Dict[str, Any]) -> str:
        """Formata lição para exibição no chat"""
        if not lesson:
            return "Lição não encontrada."
        
        text = f"⚽ **Nova Palavra:**\n\n"
        text += f"🇧🇷 **Português:** {lesson['pt']}\n"
        text += f"🇺🇸 **Inglês:** {lesson['en']}\n"
        
        if lesson.get('pronunciation'):
            text += f"🗣️ **Pronúncia:** {lesson['pronunciation']}\n"
        
        if lesson.get('explanation'):
            text += f"\n💡 **Explicação:** {lesson['explanation']}\n"
        
        if lesson.get('example_pt') and lesson.get('example_en'):
            text += f"\n📝 **Exemplo:**\n"
            text += f"PT: {lesson['example_pt']}\n"
            text += f"EN: {lesson['example_en']}\n"
        
        if lesson.get('tips'):
            text += f"\n🎯 **Dica:** {lesson['tips']}"
        
        return text

# Instância global para fácil acesso
lesson_manager = LessonManager()
content_helper = ContentHelper()