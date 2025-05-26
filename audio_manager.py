"""
🎵 FutEnglish Audio Manager
Sistema de TTS dual-language (PT-BR + EN-US) para Telegram
"""

import os
import asyncio
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import logging
from datetime import datetime, timedelta

from google.cloud import texttospeech
from google.api_core import exceptions as google_exceptions

from config import Config

logger = logging.getLogger(__name__)

class AudioCache:
    """Cache simples para arquivos de áudio"""
    
    def __init__(self, max_size: int = 100, ttl_hours: int = 1):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
    
    def _generate_key(self, text: str, language: str) -> str:
        """Gera chave única para cache"""
        import hashlib
        key_string = f"{text}_{language}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, text: str, language: str) -> Optional[str]:
        """Busca arquivo no cache"""
        key = self._generate_key(text, language)
        
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < self.ttl:
                if os.path.exists(entry['file_path']):
                    return entry['file_path']
                else:
                    # Arquivo foi removido, remove do cache
                    del self.cache[key]
        
        return None
    
    def set(self, text: str, language: str, file_path: str):
        """Adiciona arquivo ao cache"""
        key = self._generate_key(text, language)
        
        # Remove entradas antigas se necessário
        if len(self.cache) >= self.max_size:
            self._cleanup_old_entries()
        
        self.cache[key] = {
            'file_path': file_path,
            'timestamp': datetime.now()
        }
    
    def _cleanup_old_entries(self):
        """Remove entradas antigas do cache"""
        now = datetime.now()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if now - entry['timestamp'] > self.ttl:
                expired_keys.append(key)
                # Remove arquivo físico se existir
                try:
                    if os.path.exists(entry['file_path']):
                        os.unlink(entry['file_path'])
                except OSError:
                    pass
        
        for key in expired_keys:
            del self.cache[key]

class TTSEngine:
    """Engine de Text-to-Speech usando Google Cloud TTS"""
    
    def __init__(self):
        self.client = None
        self.cache = AudioCache()
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa cliente Google TTS"""
        try:
            self.client = texttospeech.TextToSpeechClient()
            logger.info("✅ Google TTS client inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Google TTS: {e}")
            self.client = None
    
    def _get_voice_config(self, language: str) -> Dict[str, Any]:
        """Retorna configuração de voz baseada no idioma"""
        if language == 'pt-BR':
            return Config.TTS_PT_CONFIG
        elif language == 'en-US':
            return Config.TTS_EN_CONFIG
        else:
            raise ValueError(f"Idioma não suportado: {language}")
    
    async def generate_audio(self, text: str, language: str) -> Optional[str]:
        """
        Gera áudio TTS e retorna caminho do arquivo
        
        Args:
            text: Texto para conversão
            language: 'pt-BR' ou 'en-US'
            
        Returns:
            Caminho do arquivo de áudio ou None em caso de erro
        """
        if not self.client:
            logger.error("Cliente TTS não inicializado")
            return None
        
        if not text.strip():
            logger.warning("Texto vazio fornecido para TTS")
            return None
        
        # Verifica cache primeiro
        cached_file = self.cache.get(text, language)
        if cached_file:
            logger.info(f"🎵 Áudio encontrado no cache: {language}")
            return cached_file
        
        try:
            # Limpa texto para TTS
            from content import ContentHelper
            clean_text = ContentHelper.clean_text_for_tts(text)
            
            # Configurações de voz
            voice_config = self._get_voice_config(language)
            
            # Input de síntese
            synthesis_input = texttospeech.SynthesisInput(text=clean_text)
            
            # Configuração de voz
            voice = texttospeech.VoiceSelectionParams(
                language_code=voice_config['language_code'],
                name=voice_config['name'],
                ssml_gender=getattr(texttospeech.SsmlVoiceGender, voice_config['ssml_gender'])
            )
            
            # Configuração de áudio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=getattr(texttospeech.AudioEncoding, Config.AUDIO_CONFIG['audio_encoding']),
                sample_rate_hertz=Config.AUDIO_CONFIG['sample_rate_hertz'],
                speaking_rate=voice_config['speaking_rate'],
                pitch=voice_config['pitch'],
                volume_gain_db=voice_config['volume_gain_db'],
                effects_profile_id=Config.AUDIO_CONFIG['effects_profile_id']
            )
            
            # Executa síntese
            logger.info(f"🎵 Gerando áudio TTS: {language} - '{clean_text[:50]}...'")
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
            )
            
            # Salva arquivo temporário
            file_path = await self._save_audio_file(response.audio_content, language)
            
            if file_path:
                # Adiciona ao cache
                self.cache.set(text, language, file_path)
                logger.info(f"✅ Áudio gerado com sucesso: {language}")
                return file_path
            
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"❌ Erro Google TTS API: {e}")
        except Exception as e:
            logger.error(f"❌ Erro inesperado no TTS: {e}")
        
        return None
    
    async def _save_audio_file(self, audio_content: bytes, language: str) -> Optional[str]:
        """Salva conteúdo de áudio em arquivo temporário"""
        try:
            # Cria arquivo temporário
            suffix = f"_{language}_{datetime.now().strftime('%H%M%S')}.ogg"
            
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
                dir=Config.TEMP_AUDIO_DIR
            ) as temp_file:
                temp_file.write(audio_content)
                return temp_file.name
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar arquivo de áudio: {e}")
            return None

class DualLanguageAudioManager:
    """Gerenciador de áudio dual-language para FutEnglish"""
    
    def __init__(self):
        self.tts_engine = TTSEngine()
        self.last_audio_files: Dict[int, Dict[str, str]] = {}  # user_id -> {pt: path, en: path}
    
    async def generate_lesson_audio(self, user_id: int, pt_text: str, en_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Gera áudios para lição (português + inglês)
        
        Args:
            user_id: ID do usuário
            pt_text: Texto em português
            en_text: Texto em inglês
            
        Returns:
            Tupla (caminho_pt, caminho_en)
        """
        logger.info(f"🎵 Gerando áudio dual para usuário {user_id}")
        
        # Gera áudios em paralelo
        tasks = [
            self.tts_engine.generate_audio(pt_text, 'pt-BR'),
            self.tts_engine.generate_audio(en_text, 'en-US')
        ]
        
        try:
            pt_path, en_path = await asyncio.gather(*tasks)
            
            # Armazena caminhos para repetição
            self.last_audio_files[user_id] = {
                'pt': pt_path,
                'en': en_path,
                'pt_text': pt_text,
                'en_text': en_text
            }
            
            return pt_path, en_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar áudio dual: {e}")
            return None, None
    
    async def generate_professor_audio(self, user_id: int, text: str) -> Optional[str]:
        """
        Gera áudio do professor (apenas português)
        
        Args:
            user_id: ID do usuário
            text: Texto do professor
            
        Returns:
            Caminho do arquivo de áudio
        """
        logger.info(f"🎵 Gerando áudio do professor para usuário {user_id}")
        
        pt_path = await self.tts_engine.generate_audio(text, 'pt-BR')
        
        if pt_path:
            # Armazena para repetição
            self.last_audio_files[user_id] = {
                'pt': pt_path,
                'en': None,
                'pt_text': text,
                'en_text': None
            }
        
        return pt_path
    
    async def repeat_last_audio(self, user_id: int) -> Tuple[Optional[str], Optional[str]]:
        """
        Repete último áudio gerado para o usuário
        
        Returns:
            Tupla (caminho_pt, caminho_en)
        """
        if user_id not in self.last_audio_files:
            return None, None
        
        last_audio = self.last_audio_files[user_id]
        
        # Verifica se arquivos ainda existem
        pt_path = last_audio.get('pt')
        en_path = last_audio.get('en')
        
        pt_exists = pt_path and os.path.exists(pt_path)
        en_exists = en_path and os.path.exists(en_path)
        
        # Se arquivos não existem mais, regenera
        if not pt_exists or (en_path and not en_exists):
            logger.info("🔄 Regenerando áudios removidos")
            
            pt_text = last_audio.get('pt_text')
            en_text = last_audio.get('en_text')
            
            if pt_text and en_text:
                return await self.generate_lesson_audio(user_id, pt_text, en_text)
            elif pt_text:
                pt_new = await self.generate_professor_audio(user_id, pt_text)
                return pt_new, None
        
        return (pt_path if pt_exists else None), (en_path if en_exists else None)
    
    async def cleanup_user_audio(self, user_id: int):
        """Remove áudios temporários do usuário"""
        if user_id in self.last_audio_files:
            last_audio = self.last_audio_files[user_id]
            
            for path in [last_audio.get('pt'), last_audio.get('en')]:
                if path and os.path.exists(path):
                    try:
                        os.unlink(path)
                        logger.info(f"🗑️ Áudio removido: {path}")
                    except OSError as e:
                        logger.warning(f"⚠️ Erro ao remover áudio: {e}")
            
            del self.last_audio_files[user_id]
    
    async def cleanup_old_audio_files(self):
        """Remove arquivos de áudio antigos"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)
            removed_count = 0
            
            for file_path in Config.TEMP_AUDIO_DIR.glob("*.ogg"):
                if file_path.stat().st_mtime < cutoff_time.timestamp():
                    try:
                        file_path.unlink()
                        removed_count += 1
                    except OSError:
                        pass
            
            if removed_count > 0:
                logger.info(f"🧹 Limpeza: {removed_count} arquivos de áudio antigos removidos")
                
        except Exception as e:
            logger.error(f"❌ Erro na limpeza de áudios: {e}")
    
    def get_audio_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de áudio"""
        return {
            'users_with_audio': len(self.last_audio_files),
            'cache_size': len(self.tts_engine.cache.cache),
            'temp_files': len(list(Config.TEMP_AUDIO_DIR.glob("*.ogg"))),
            'tts_available': self.tts_engine.client is not None
        }

# Instância global
audio_manager = DualLanguageAudioManager()