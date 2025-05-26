"""
👤 FutEnglish User State Manager
Gerencia estado, sessões e progresso dos usuários
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import threading
import time

logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    """Estrutura de dados para sessão do usuário"""
    
    # Dados pessoais
    user_id: int
    name: str = ""
    position: str = ""
    english_level: str = "Intermediário"
    
    # Estado atual
    current_step: str = "onboarding"  # onboarding, lesson, chat
    current_lesson_id: int = 1
    last_audio_text: str = ""
    last_interaction: datetime = field(default_factory=datetime.now)
    
    # Progresso (fake para demonstração)
    lessons_completed: list = field(default_factory=list)
    total_interactions: int = 0
    session_start: datetime = field(default_factory=datetime.now)
    
    # Controle de fluxo
    waiting_for_name: bool = False
    waiting_for_position: bool = False  
    waiting_for_level: bool = False
    onboarding_complete: bool = False
    
    # Rate limiting
    message_timestamps: list = field(default_factory=list)
    
    def update_last_interaction(self):
        """Atualiza timestamp da última interação"""
        self.last_interaction = datetime.now()
        self.total_interactions += 1
    
    def add_message_timestamp(self):
        """Adiciona timestamp para controle de rate limiting"""
        now = datetime.now()
        self.message_timestamps.append(now)
        
        # Remove timestamps mais antigos que 1 minuto
        cutoff = now - timedelta(minutes=1)
        self.message_timestamps = [ts for ts in self.message_timestamps if ts > cutoff]
    
    def is_rate_limited(self, max_messages: int = 10) -> bool:
        """Verifica se usuário está sendo rate limited"""
        self.add_message_timestamp()
        return len(self.message_timestamps) > max_messages
    
    def get_session_duration(self) -> timedelta:
        """Retorna duração da sessão atual"""
        return datetime.now() - self.session_start
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte sessão para dicionário"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'position': self.position, 
            'english_level': self.english_level,
            'current_step': self.current_step,
            'current_lesson_id': self.current_lesson_id,
            'onboarding_complete': self.onboarding_complete,
            'total_interactions': self.total_interactions,
            'session_duration': str(self.get_session_duration())
        }

class UserStateManager:
    """Gerenciador central de estado dos usuários"""
    
    def __init__(self):
        self.sessions: Dict[int, UserSession] = {}
        self.lock = threading.Lock()
        self._cleanup_task_running = False
        self._start_cleanup_task()
    
    def get_or_create_session(self, user_id: int) -> UserSession:
        """Obtém sessão existente ou cria nova"""
        with self.lock:
            if user_id not in self.sessions:
                self.sessions[user_id] = UserSession(user_id=user_id)
            else:
                # Atualiza última interação
                self.sessions[user_id].update_last_interaction()
            
            return self.sessions[user_id]
    
    def update_session(self, user_id: int, **kwargs) -> UserSession:
        """Atualiza dados da sessão"""
        logger.info(f"🔄 update_session() para usuário {user_id} com {len(kwargs)} parâmetros")
        
        try:
            logger.info("🔒 Adquirindo lock...")
            with self.lock:
                logger.info("✅ Lock adquirido!")
                
                logger.info("📊 Obtendo ou criando sessão...")
                session = self.get_or_create_session(user_id)
                logger.info(f"✅ Sessão obtida: {session.user_id}")
                
                logger.info(f"🔧 Atualizando {len(kwargs)} atributos...")
                for key, value in kwargs.items():
                    logger.info(f"  ➤ {key} = {value}")
                    if hasattr(session, key):
                        setattr(session, key, value)
                    else:
                        logger.warning(f"⚠️ Atributo {key} não existe na sessão")
                
                logger.info("⏰ Atualizando timestamp...")
                session.update_last_interaction()
                logger.info("✅ Sessão atualizada com sucesso!")
                
                return session
        except Exception as e:
            logger.error(f"❌ Erro em update_session: {e}")
            raise
    
    def get_session(self, user_id: int) -> Optional[UserSession]:
        """Obtém sessão existente sem criar nova"""
        with self.lock:
            return self.sessions.get(user_id)
    
    def delete_session(self, user_id: int) -> bool:
        """Remove sessão do usuário"""
        with self.lock:
            if user_id in self.sessions:
                del self.sessions[user_id]
                return True
            return False
    
    def is_user_rate_limited(self, user_id: int) -> bool:
        """Verifica rate limiting para usuário"""
        session = self.get_or_create_session(user_id)
        return session.is_rate_limited()
    
    def get_all_sessions_count(self) -> int:
        """Retorna número total de sessões ativas"""
        with self.lock:
            return len(self.sessions)
    
    def get_session_stats(self, user_id: int) -> Dict[str, Any]:
        """Retorna estatísticas da sessão"""
        session = self.get_session(user_id)
        if not session:
            return {}
        
        return {
            'name': session.name,
            'position': session.position,
            'level': session.english_level,
            'current_lesson': session.current_lesson_id,
            'interactions': session.total_interactions,
            'session_duration': str(session.get_session_duration()),
            'lessons_completed': len(session.lessons_completed),
            'onboarding_complete': session.onboarding_complete
        }
    
    def _cleanup_old_sessions(self):
        """Remove sessões inativas há mais de 1 hora"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        with self.lock:
            inactive_users = []
            for user_id, session in self.sessions.items():
                if session.last_interaction < cutoff_time:
                    inactive_users.append(user_id)
            
            for user_id in inactive_users:
                del self.sessions[user_id]
        
        if inactive_users:
            print(f"🧹 Limpeza: {len(inactive_users)} sessões inativas removidas")
    
    def _start_cleanup_task(self):
        """Inicia task de limpeza automática"""
        if self._cleanup_task_running:
            return
        
        def cleanup_loop():
            self._cleanup_task_running = True
            while self._cleanup_task_running:
                time.sleep(3600)  # 1 hora
                self._cleanup_old_sessions()
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def stop_cleanup_task(self):
        """Para task de limpeza"""
        self._cleanup_task_running = False

class OnboardingFlow:
    """Gerencia fluxo de onboarding dos usuários"""
    
    POSITIONS = [
        "Goleiro", "Zagueiro", "Lateral", "Volante", 
        "Meio-campo", "Atacante", "Não jogo, só assisto"
    ]
    
    ENGLISH_LEVELS = ["Iniciante", "Intermediário", "Avançado"]
    
    def __init__(self, state_manager: UserStateManager):
        self.state_manager = state_manager
    
    def start_onboarding(self, user_id: int) -> str:
        """Inicia processo de onboarding"""
        logger.info(f"🔄 start_onboarding() chamada para usuário {user_id}")
        
        try:
            logger.info("📊 Atualizando sessão do usuário...")
            session = self.state_manager.update_session(
                user_id,
                current_step="onboarding",
                waiting_for_name=True,
                onboarding_complete=False
            )
            logger.info(f"✅ Sessão atualizada: {session.user_id}")
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar sessão: {e}")
            raise
        
        logger.info("📝 Gerando texto de boas-vindas...")
        
        welcome_text = """
🔥 Eaí, futuro craque! Sou o Professor Bola Gringa! ⚽

Vou te ensinar inglês usando o que você mais ama: FUTEBOL! 
Aqui você vai aprender vocabulário, gírias e tudo sobre o beautiful game em inglês!

Vamos começar se conhecendo melhor? 

**Qual é o seu nome?** 😎
"""
        
        logger.info("✅ Texto de boas-vindas gerado com sucesso!")
        return welcome_text
    
    def process_onboarding_input(self, user_id: int, message: str) -> tuple[str, bool]:
        """
        Processa entrada durante onboarding
        Retorna: (resposta, onboarding_completo)
        """
        session = self.state_manager.get_session(user_id)
        if not session:
            return self.start_onboarding(user_id), False
        
        # Aguardando nome
        if session.waiting_for_name:
            return self._handle_name_input(user_id, message)
        
        # Aguardando posição
        elif session.waiting_for_position:
            return self._handle_position_input(user_id, message)
        
        # Aguardando nível de inglês
        elif session.waiting_for_level:
            return self._handle_level_input(user_id, message)
        
        return "Algo deu errado no onboarding. Vamos recomeçar!", False
    
    def _handle_name_input(self, user_id: int, name: str) -> tuple[str, bool]:
        """Processa entrada do nome"""
        name = name.strip()
        
        if len(name) < 2:
            return "Por favor, digite um nome válido:", False
        
        self.state_manager.update_session(
            user_id,
            name=name,
            waiting_for_name=False,
            waiting_for_position=True
        )
        
        positions_text = "\n".join([f"{i+1}. {pos}" for i, pos in enumerate(self.POSITIONS)])
        
        return f"""
Prazer em te conhecer, {name}! 🤝

Agora me conta: **qual posição você joga?**
(ou qual você mais gosta de assistir)

{positions_text}

Digite o número ou o nome da posição:
""", False
    
    def _handle_position_input(self, user_id: int, position_input: str) -> tuple[str, bool]:
        """Processa entrada da posição"""
        position_input = position_input.strip()
        position = None
        
        # Tenta interpretar como número
        try:
            pos_index = int(position_input) - 1
            if 0 <= pos_index < len(self.POSITIONS):
                position = self.POSITIONS[pos_index]
        except ValueError:
            pass
        
        # Tenta encontrar por nome
        if not position:
            position_lower = position_input.lower()
            for pos in self.POSITIONS:
                if pos.lower() in position_lower or position_lower in pos.lower():
                    position = pos
                    break
        
        if not position:
            positions_text = "\n".join([f"{i+1}. {pos}" for i, pos in enumerate(self.POSITIONS)])
            return f"""
Não entendi a posição. Escolha uma das opções:

{positions_text}

Digite o número ou nome:
""", False
        
        self.state_manager.update_session(
            user_id,
            position=position,
            waiting_for_position=False,
            waiting_for_level=True
        )
        
        levels_text = "\n".join([f"{i+1}. {level}" for i, level in enumerate(self.ENGLISH_LEVELS)])
        
        return f"""
Que massa! {position} é uma posição importante! ⚽

Agora me conta: **qual seu nível de inglês?**

{levels_text}

Digite o número ou nome do nível:
""", False
    
    def _handle_level_input(self, user_id: int, level_input: str) -> tuple[str, bool]:
        """Processa entrada do nível de inglês"""
        level_input = level_input.strip()
        level = None
        
        # Tenta interpretar como número
        try:
            level_index = int(level_input) - 1
            if 0 <= level_index < len(self.ENGLISH_LEVELS):
                level = self.ENGLISH_LEVELS[level_index]
        except ValueError:
            pass
        
        # Tenta encontrar por nome
        if not level:
            level_lower = level_input.lower()
            for lv in self.ENGLISH_LEVELS:
                if lv.lower() in level_lower or level_lower in lv.lower():
                    level = lv
                    break
        
        if not level:
            levels_text = "\n".join([f"{i+1}. {lv}" for i, lv in enumerate(self.ENGLISH_LEVELS)])
            return f"""
Não entendi o nível. Escolha uma das opções:

{levels_text}

Digite o número ou nome:
""", False
        
        session = self.state_manager.update_session(
            user_id,
            english_level=level,
            waiting_for_level=False,
            onboarding_complete=True,
            current_step="lesson"
        )
        
        return f"""
Perfeito, {session.name}! 🎉

**Seu Perfil:**
👤 Nome: {session.name}
⚽ Posição: {session.position}  
📚 Nível: {session.english_level}

Agora vamos começar a aprender inglês com futebol! 
Use /próxima para começar sua primeira lição, ou conversе comigo livremente sobre futebol!

Bora que bora! 🚀⚽
""", True

class StateValidator:
    """Validador de estado e consistência"""
    
    @staticmethod
    def validate_session(session: UserSession) -> bool:
        """Valida consistência da sessão"""
        if not session:
            return False
        
        # Validações básicas
        if session.user_id <= 0:
            return False
        
        if session.onboarding_complete:
            if not session.name or not session.position or not session.english_level:
                return False
        
        if session.current_lesson_id < 1:
            session.current_lesson_id = 1
        
        return True
    
    @staticmethod
    def sanitize_user_input(text: str) -> str:
        """Limpa entrada do usuário"""
        if not text:
            return ""
        
        # Remove caracteres perigosos
        text = text.strip()
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Limita tamanho
        if len(text) > 500:
            text = text[:500]
        
        return text

# Instâncias globais
user_state_manager = UserStateManager()
onboarding_flow = OnboardingFlow(user_state_manager)