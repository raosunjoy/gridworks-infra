"""
Advanced Voice Processing Engine
Indian accent recognition, multilingual speech processing, and conversational AI
"""

import asyncio
import logging
import io
import wave
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
import librosa
import soundfile as sf
from dataclasses import dataclass
from enum import Enum
import aiofiles
import openai
import speech_recognition as sr
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
import webrtcvad

from app.core.config import settings
from app.core.enterprise_architecture import PerformanceConfig, ServiceTier

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    M4A = "m4a"
    OPUS = "opus"


class IndianAccent(Enum):
    NORTH_INDIAN = "north_indian"
    SOUTH_INDIAN = "south_indian"
    WEST_INDIAN = "west_indian"
    EAST_INDIAN = "east_indian"
    GENERIC_INDIAN = "generic_indian"


class Language(Enum):
    HINDI = "hi"
    ENGLISH = "en"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    URDU = "ur"
    MIXED = "mixed"  # Code-mixed languages


@dataclass
class VoiceAnalysis:
    """Comprehensive voice analysis results"""
    text: str
    language: Language
    confidence: float
    accent: IndianAccent
    emotion: str
    speaking_rate: float
    audio_quality: float
    background_noise: float
    speaker_gender: str
    processing_time_ms: float
    trading_intent: Optional[str] = None
    extracted_entities: Dict[str, Any] = None


class VoiceProcessor:
    """
    Advanced voice processing with Indian accent optimization
    Supports 11 Indian languages with accent detection
    """
    
    def __init__(self):
        # Performance configuration
        self.performance_config = PerformanceConfig(
            max_response_time_ms=3000,  # 3 seconds for voice processing
            max_concurrent_requests=1000,
            cache_ttl_seconds=300,
            rate_limit_per_minute=100,
            circuit_breaker_threshold=3,
            service_tier=ServiceTier.HIGH
        )
        
        # Audio processing parameters
        self.audio_params = {
            'sample_rate': 16000,
            'channels': 1,
            'bit_depth': 16,
            'chunk_size': 1024,
            'max_duration': 60,  # 60 seconds max
            'min_duration': 0.5,  # 0.5 seconds min
            'silence_threshold': 0.01,
            'noise_reduction': True
        }
        
        # Indian accent models and patterns
        self.accent_models = {
            IndianAccent.NORTH_INDIAN: {
                'phonetic_patterns': ['th->d', 'v->w', 'z->j'],
                'intonation_pattern': 'rising_falling',
                'stress_pattern': 'syllable_timed'
            },
            IndianAccent.SOUTH_INDIAN: {
                'phonetic_patterns': ['p->b', 'k->g', 'retroflex_emphasis'],
                'intonation_pattern': 'flat_rising',
                'stress_pattern': 'mora_timed'
            },
            IndianAccent.WEST_INDIAN: {
                'phonetic_patterns': ['aspirated_emphasis', 'r_rolling'],
                'intonation_pattern': 'variable',
                'stress_pattern': 'stress_timed'
            },
            IndianAccent.EAST_INDIAN: {
                'phonetic_patterns': ['sh->s', 'ch->c', 'soft_consonants'],
                'intonation_pattern': 'melodic',
                'stress_pattern': 'syllable_timed'
            }
        }
        
        # Language detection patterns
        self.language_patterns = {
            Language.HINDI: {
                'keywords': ['kya', 'hai', 'mein', 'aur', 'ka', 'ki', 'ko', 'se'],
                'script_markers': ['devanagari'],
                'phonemes': ['retroflex', 'aspirated']
            },
            Language.TAMIL: {
                'keywords': ['enna', 'irukku', 'illa', 'vandhu', 'poga'],
                'script_markers': ['tamil'],
                'phonemes': ['retroflex_heavy', 'no_aspirated']
            },
            Language.TELUGU: {
                'keywords': ['enti', 'unnadi', 'ledu', 'vachchi', 'vellu'],
                'script_markers': ['telugu'],
                'phonemes': ['retroflex', 'gemination']
            },
            Language.BENGALI: {
                'keywords': ['ki', 'ache', 'nei', 'eshche', 'jabo'],
                'script_markers': ['bengali'],
                'phonemes': ['soft_consonants', 'vowel_harmony']
            }
        }
        
        # Trading vocabulary for intent detection
        self.trading_vocabulary = {
            'english': {
                'buy': ['buy', 'purchase', 'invest', 'get', 'acquire'],
                'sell': ['sell', 'exit', 'book', 'square off', 'close'],
                'stocks': ['stock', 'share', 'equity', 'scrip'],
                'quantity': ['shares', 'lots', 'pieces', 'units'],
                'portfolio': ['portfolio', 'holdings', 'positions'],
                'market': ['market', 'sensex', 'nifty', 'index']
            },
            'hindi': {
                'buy': ['khareedna', 'lena', 'invest karna'],
                'sell': ['bechna', 'nikalna', 'band karna'],
                'stocks': ['share', 'stock', 'company'],
                'quantity': ['kitna', 'quantity', 'amount'],
                'portfolio': ['portfolio', 'investment'],
                'market': ['market', 'bazaar', 'stock market']
            },
            'tamil': {
                'buy': ['vanga', 'kolla', 'invest pannu'],
                'sell': ['vikka', 'vitu', 'close pannu'],
                'stocks': ['share', 'stock', 'company'],
                'portfolio': ['portfolio', 'investment'],
                'market': ['market', 'share market']
            }
        }
        
        # Voice Activity Detection
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        
        # Initialize speech recognition engines
        self.recognizers = {
            'whisper': None,  # OpenAI Whisper
            'google': sr.Recognizer(),  # Google Speech API
            'azure': None,  # Azure Speech Services
            'indian_asr': None  # Custom Indian ASR model
        }
        
        # Cache for performance
        self.audio_cache = {}
        self.accent_cache = {}
    
    async def initialize(self):
        """Initialize voice processing engine"""
        
        try:
            logger.info("🎤 Initializing Voice Processing Engine...")
            
            # Initialize Whisper model
            await self._initialize_whisper()
            
            # Load Indian accent models
            await self._load_accent_models()
            
            # Initialize language detection
            await self._initialize_language_detection()
            
            # Setup audio processing pipeline
            await self._setup_audio_pipeline()
            
            logger.info("✅ Voice Processing Engine initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Voice Processing: {str(e)}")
            raise
    
    async def process_voice_message(
        self,
        audio_data: bytes,
        user_id: str,
        audio_format: AudioFormat = AudioFormat.OGG
    ) -> VoiceAnalysis:
        """Process voice message with comprehensive analysis"""
        
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"🎤 Processing voice message for user {user_id}")
            
            # Validate audio data
            if not audio_data or len(audio_data) < 1000:  # Minimum 1KB
                raise ValueError("Invalid or empty audio data")
            
            # Convert and preprocess audio
            processed_audio = await self._preprocess_audio(audio_data, audio_format)
            
            # Parallel processing for speed
            analysis_tasks = [
                self._transcribe_audio(processed_audio),
                self._detect_language(processed_audio),
                self._detect_accent(processed_audio),
                self._analyze_audio_features(processed_audio),
                self._detect_emotion(processed_audio),
                self._measure_audio_quality(processed_audio)
            ]
            
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Process results
            transcription = results[0] if not isinstance(results[0], Exception) else ""
            language_info = results[1] if not isinstance(results[1], Exception) else {'language': Language.ENGLISH, 'confidence': 0.5}
            accent_info = results[2] if not isinstance(results[2], Exception) else {'accent': IndianAccent.GENERIC_INDIAN, 'confidence': 0.5}
            audio_features = results[3] if not isinstance(results[3], Exception) else {}
            emotion_info = results[4] if not isinstance(results[4], Exception) else {'emotion': 'neutral', 'confidence': 0.5}
            quality_info = results[5] if not isinstance(results[5], Exception) else {'quality': 0.7, 'noise': 0.3}
            
            # Extract trading intent and entities
            trading_intent = await self._extract_trading_intent(transcription, language_info['language'])
            entities = await self._extract_entities(transcription, language_info['language'])
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create voice analysis result
            voice_analysis = VoiceAnalysis(
                text=transcription,
                language=language_info['language'],
                confidence=language_info['confidence'],
                accent=accent_info['accent'],
                emotion=emotion_info['emotion'],
                speaking_rate=audio_features.get('speaking_rate', 0),
                audio_quality=quality_info['quality'],
                background_noise=quality_info['noise'],
                speaker_gender=audio_features.get('gender', 'unknown'),
                processing_time_ms=processing_time,
                trading_intent=trading_intent,
                extracted_entities=entities
            )
            
            # Cache results for performance
            cache_key = f"voice_{user_id}_{hash(audio_data[:1000])}"
            self.audio_cache[cache_key] = {
                'analysis': voice_analysis,
                'timestamp': datetime.utcnow(),
                'ttl': 3600  # 1 hour
            }
            
            logger.info(f"✅ Voice processing completed in {processing_time:.1f}ms")
            return voice_analysis
            
        except Exception as e:
            logger.error(f"❌ Error processing voice message: {str(e)}")
            return VoiceAnalysis(
                text="Sorry, I couldn't understand the audio message.",
                language=Language.ENGLISH,
                confidence=0.0,
                accent=IndianAccent.GENERIC_INDIAN,
                emotion="unknown",
                speaking_rate=0,
                audio_quality=0,
                background_noise=1.0,
                speaker_gender="unknown",
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
    
    async def _preprocess_audio(self, audio_data: bytes, audio_format: AudioFormat) -> np.ndarray:
        """Preprocess audio for optimal recognition"""
        
        try:
            # Convert to AudioSegment
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=audio_format.value)
            
            # Normalize audio
            audio = normalize(audio)
            
            # Apply dynamic range compression
            audio = compress_dynamic_range(audio)
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Resample to 16kHz
            if audio.frame_rate != self.audio_params['sample_rate']:
                audio = audio.set_frame_rate(self.audio_params['sample_rate'])
            
            # Apply noise reduction if enabled
            if self.audio_params['noise_reduction']:
                audio = await self._apply_noise_reduction(audio)
            
            # Convert to numpy array
            audio_array = np.array(audio.get_array_of_samples(), dtype=np.float32)
            audio_array = audio_array / 32768.0  # Normalize to [-1, 1]
            
            return audio_array
            
        except Exception as e:
            logger.error(f"❌ Error preprocessing audio: {str(e)}")
            raise
    
    async def _transcribe_audio(self, audio_array: np.ndarray) -> str:
        """Transcribe audio using multiple ASR engines for accuracy"""
        
        try:
            # Primary: OpenAI Whisper (best for Indian accents)
            whisper_result = await self._transcribe_with_whisper(audio_array)
            
            if whisper_result and len(whisper_result.strip()) > 0:
                return whisper_result
            
            # Fallback: Google Speech API
            google_result = await self._transcribe_with_google(audio_array)
            
            if google_result and len(google_result.strip()) > 0:
                return google_result
            
            # Last resort: Basic speech recognition
            return await self._transcribe_basic(audio_array)
            
        except Exception as e:
            logger.error(f"❌ Error transcribing audio: {str(e)}")
            return ""
    
    async def _transcribe_with_whisper(self, audio_array: np.ndarray) -> str:
        """Transcribe using OpenAI Whisper (optimized for Indian accents)"""
        
        try:
            # Save audio to temporary buffer
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, audio_array, self.audio_params['sample_rate'], format='WAV')
            audio_buffer.seek(0)
            
            # Use Whisper API
            transcript = await openai.Audio.atranscribe(
                model="whisper-1",
                file=audio_buffer,
                response_format="text",
                language=None,  # Auto-detect
                temperature=0.2
            )
            
            return transcript.strip()
            
        except Exception as e:
            logger.error(f"❌ Whisper transcription error: {str(e)}")
            return ""
    
    async def _detect_language(self, audio_array: np.ndarray) -> Dict[str, Any]:
        """Detect language from audio with Indian language support"""
        
        try:
            # Extract audio features for language detection
            mfcc = librosa.feature.mfcc(y=audio_array, sr=self.audio_params['sample_rate'], n_mfcc=13)
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_array, sr=self.audio_params['sample_rate'])
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_array)
            
            # Basic language classification based on audio features
            # This would be replaced with a trained model in production
            
            # For now, use simple heuristics
            avg_pitch = np.mean(spectral_centroid)
            avg_zcr = np.mean(zero_crossing_rate)
            
            # Language detection heuristics (simplified)
            if avg_pitch > 1500 and avg_zcr > 0.1:
                # High pitch and variability - likely South Indian language
                detected_language = Language.TAMIL
                confidence = 0.7
            elif avg_pitch > 1200:
                # Medium-high pitch - likely Hindi
                detected_language = Language.HINDI
                confidence = 0.8
            else:
                # Default to English for mixed/unclear audio
                detected_language = Language.ENGLISH
                confidence = 0.6
            
            return {
                'language': detected_language,
                'confidence': confidence,
                'features': {
                    'pitch': avg_pitch,
                    'zero_crossing_rate': avg_zcr,
                    'mfcc_mean': np.mean(mfcc)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Language detection error: {str(e)}")
            return {'language': Language.ENGLISH, 'confidence': 0.5}
    
    async def _detect_accent(self, audio_array: np.ndarray) -> Dict[str, Any]:
        """Detect Indian accent from audio features"""
        
        try:
            # Extract prosodic features
            pitch, voiced_flag, voiced_probs = librosa.pyin(
                audio_array,
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7')
            )
            
            # Calculate pitch statistics
            pitch_mean = np.nanmean(pitch)
            pitch_std = np.nanstd(pitch)
            pitch_range = np.nanmax(pitch) - np.nanmin(pitch)
            
            # Extract formant-like features
            mfcc = librosa.feature.mfcc(y=audio_array, sr=self.audio_params['sample_rate'], n_mfcc=13)
            formant_features = np.mean(mfcc[1:4], axis=1)  # F1, F2, F3 approximation
            
            # Accent classification heuristics
            # In production, this would use a trained model
            
            if pitch_std > 50 and pitch_range > 200:
                # High pitch variation - likely South Indian
                accent = IndianAccent.SOUTH_INDIAN
                confidence = 0.75
            elif pitch_mean > 150 and formant_features[1] > 0:
                # Medium pitch with specific formant pattern - North Indian
                accent = IndianAccent.NORTH_INDIAN
                confidence = 0.7
            elif pitch_std < 30:
                # Low pitch variation - likely East Indian
                accent = IndianAccent.EAST_INDIAN
                confidence = 0.65
            else:
                # Default to generic Indian accent
                accent = IndianAccent.GENERIC_INDIAN
                confidence = 0.6
            
            return {
                'accent': accent,
                'confidence': confidence,
                'features': {
                    'pitch_mean': pitch_mean,
                    'pitch_std': pitch_std,
                    'pitch_range': pitch_range,
                    'formants': formant_features.tolist()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Accent detection error: {str(e)}")
            return {'accent': IndianAccent.GENERIC_INDIAN, 'confidence': 0.5}
    
    async def _extract_trading_intent(self, text: str, language: Language) -> Optional[str]:
        """Extract trading intent from transcribed text"""
        
        try:
            text_lower = text.lower()
            
            # Get vocabulary for detected language
            vocab = self.trading_vocabulary.get(language.value, self.trading_vocabulary['english'])
            
            # Check for trading actions
            if any(word in text_lower for word in vocab['buy']):
                return 'buy_intent'
            elif any(word in text_lower for word in vocab['sell']):
                return 'sell_intent'
            elif any(word in text_lower for word in vocab['portfolio']):
                return 'portfolio_query'
            elif any(word in text_lower for word in vocab['market']):
                return 'market_query'
            
            # Use NLP for more sophisticated intent detection
            # This would integrate with the conversation engine
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Intent extraction error: {str(e)}")
            return None
    
    async def _extract_entities(self, text: str, language: Language) -> Dict[str, Any]:
        """Extract entities like stock names, quantities, prices from text"""
        
        try:
            entities = {
                'stocks': [],
                'quantities': [],
                'prices': [],
                'timeframes': []
            }
            
            # Basic entity extraction patterns
            import re
            
            # Stock symbols (Indian stocks)
            stock_patterns = [
                r'\b(RELIANCE|TCS|HDFC|INFY|ITC|SBI|BHARTI)\b',
                r'\b(reliance|tcs|hdfc|infosys|itc|sbi|bharti)\b'
            ]
            
            for pattern in stock_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities['stocks'].extend(matches)
            
            # Quantities
            quantity_patterns = [
                r'\b(\d+)\s*(shares?|lots?|units?)\b',
                r'\b(\d+)\s*(share|lot|unit)\b'
            ]
            
            for pattern in quantity_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities['quantities'].extend([int(match[0]) for match in matches])
            
            # Prices (Indian Rupees)
            price_patterns = [
                r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',
                r'\b(\d+(?:,\d+)*(?:\.\d+)?)\s*rupees?\b'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities['prices'].extend([float(match.replace(',', '')) for match in matches])
            
            return entities
            
        except Exception as e:
            logger.error(f"❌ Entity extraction error: {str(e)}")
            return {'stocks': [], 'quantities': [], 'prices': [], 'timeframes': []}
    
    async def convert_voice_to_trading_command(self, voice_analysis: VoiceAnalysis) -> Dict[str, Any]:
        """Convert voice analysis to structured trading command"""
        
        try:
            command = {
                'type': 'voice_command',
                'original_text': voice_analysis.text,
                'language': voice_analysis.language.value,
                'confidence': voice_analysis.confidence,
                'intent': voice_analysis.trading_intent,
                'entities': voice_analysis.extracted_entities,
                'processing_metadata': {
                    'accent': voice_analysis.accent.value,
                    'emotion': voice_analysis.emotion,
                    'audio_quality': voice_analysis.audio_quality,
                    'processing_time': voice_analysis.processing_time_ms
                }
            }
            
            # Structure trading command based on intent
            if voice_analysis.trading_intent == 'buy_intent':
                command['action'] = 'buy'
                command['symbol'] = voice_analysis.extracted_entities.get('stocks', [None])[0]
                command['quantity'] = voice_analysis.extracted_entities.get('quantities', [None])[0]
                command['price'] = voice_analysis.extracted_entities.get('prices', [None])[0]
            
            elif voice_analysis.trading_intent == 'sell_intent':
                command['action'] = 'sell'
                command['symbol'] = voice_analysis.extracted_entities.get('stocks', [None])[0]
                command['quantity'] = voice_analysis.extracted_entities.get('quantities', [None])[0]
            
            elif voice_analysis.trading_intent == 'portfolio_query':
                command['action'] = 'portfolio_check'
            
            elif voice_analysis.trading_intent == 'market_query':
                command['action'] = 'market_status'
            
            return command
            
        except Exception as e:
            logger.error(f"❌ Error converting voice to command: {str(e)}")
            return {
                'type': 'voice_command',
                'error': str(e),
                'original_text': voice_analysis.text
            }
    
    # Additional helper methods for audio processing
    async def _apply_noise_reduction(self, audio: AudioSegment) -> AudioSegment:
        """Apply noise reduction to audio"""
        # Simplified noise reduction - in production would use advanced algorithms
        return audio.normalize()
    
    async def _analyze_audio_features(self, audio_array: np.ndarray) -> Dict[str, Any]:
        """Analyze various audio features"""
        
        # Speaking rate estimation
        speech_segments = librosa.effects.split(audio_array, top_db=20)
        total_speech_time = sum(len(segment) for segment in speech_segments) / self.audio_params['sample_rate']
        speaking_rate = len(speech_segments) / max(total_speech_time, 1)
        
        # Gender estimation (simplified)
        pitch, _, _ = librosa.pyin(audio_array, fmin=50, fmax=400)
        avg_pitch = np.nanmean(pitch)
        gender = 'female' if avg_pitch > 165 else 'male' if avg_pitch > 85 else 'unknown'
        
        return {
            'speaking_rate': speaking_rate,
            'gender': gender,
            'speech_duration': total_speech_time
        }
    
    async def _detect_emotion(self, audio_array: np.ndarray) -> Dict[str, Any]:
        """Detect emotion from voice"""
        
        # Simplified emotion detection based on prosodic features
        # In production, would use trained emotion recognition model
        
        pitch, _, _ = librosa.pyin(audio_array, fmin=50, fmax=400)
        energy = librosa.feature.rms(y=audio_array)[0]
        
        pitch_var = np.nanvar(pitch)
        energy_mean = np.mean(energy)
        
        # Simple heuristics
        if pitch_var > 1000 and energy_mean > 0.1:
            emotion = 'excited'
        elif pitch_var < 500 and energy_mean < 0.05:
            emotion = 'calm'
        elif energy_mean > 0.15:
            emotion = 'confident'
        else:
            emotion = 'neutral'
        
        return {'emotion': emotion, 'confidence': 0.6}
    
    async def _measure_audio_quality(self, audio_array: np.ndarray) -> Dict[str, float]:
        """Measure audio quality metrics"""
        
        # Signal-to-noise ratio estimation
        signal_power = np.mean(audio_array ** 2)
        noise_power = np.var(audio_array)
        snr = 10 * np.log10(signal_power / max(noise_power, 1e-10))
        
        # Quality score (0-1)
        quality = min(max((snr - 10) / 20, 0), 1)
        noise = 1 - quality
        
        return {'quality': quality, 'noise': noise, 'snr': snr}