import sys
from src.core.config import load_config, get_available_personalities, get_default_personality, get_personality_system_prompt, get_personality_voice, get_ollama_url, get_default_model
from src.core.llm import OllamaClient
from src.core.storage import Storage
from src.core.logger import init_logging, log_config, log_error, get_log_file_path
from src.voice import stt
from src.voice import tts


def select_personality():
    personalities = get_available_personalities()
    default = get_default_personality()
    
    print("Available personalities:", ", ".join(personalities), flush=True)
    print(f"Default: {default}", flush=True)
    
    while True:
        choice = input("Select personality (press Enter for default): ").strip().lower()
        
        if not choice:
            return default
        
        if choice in personalities:
            return choice
        
        print(f"Invalid choice. Available: {', '.join(personalities)}", flush=True)


def voice_mode(client: OllamaClient, storage: Storage, conversation_id: int):
    print("\n[Voice mode activated]", flush=True)
    print("Press Enter to start recording, type 'stop' to return to text mode\n", flush=True)
    
    stt.init_whisper("small")
    tts.init_piper()
    
    while True:
        try:
            print("Press Enter to speak (or 'stop' to exit voice mode): ", end="", flush=True)
            cmd = input().strip().lower()
            
            if cmd == "stop" or cmd == "s":
                print("[Voice mode deactivated]\n", flush=True)
                break
            
            print("Listening...", flush=True)
            
            text = stt.transcribe_from_mic()
            
            if not text:
                print("No speech detected. Try again.", flush=True)
                continue
            
            print(f"You (voice): {text}", flush=True)
            
            storage.add_message(conversation_id, "user", text)
            
            context = storage.get_conversation(conversation_id)
            response = client.generate(text, context)
            
            storage.add_message(conversation_id, "assistant", response)
            
            print(f"Ava: {response}\n", flush=True)
            
            print("Speaking...", flush=True)
            tts.speak(response)
            
        except KeyboardInterrupt:
            print("\n[Voice mode deactivated]", flush=True)
            break
        except Exception as e:
            log_error(e, "voice_mode")
            print(f"Error: {e}", flush=True)


def talk_mode(client: OllamaClient, storage: Storage, conversation_id: int, voice: str):
    print(f"\n[Talk mode enabled - Ava will speak her responses]", flush=True)
    print("Type 'stop' to return to silent mode\n", flush=True)
    
    import pygame
    # pygame.mixer.init(frequency=22050)
    pygame.mixer.init(frequency=44100, size=-16, channels=2)
    
    tts.init_piper(voice)
    
    while True:
        try:
            print("You: ", end="", flush=True)
            user_input = input().strip()
            
            if user_input.lower() == "stop" or user_input.lower() == "s":
                print("[Talk mode disabled]\n", flush=True)
                break
            
            if user_input.lower() == "exit":
                print("Goodbye!", flush=True)
                exit()
            
            if not user_input:
                continue
            
            storage.add_message(conversation_id, "user", user_input)
            
            context = storage.get_conversation(conversation_id)
            response = client.generate(user_input, context)
            
            storage.add_message(conversation_id, "assistant", response)
            
            print(f"Ava: {response}\n", flush=True)
            
            print("Speaking...", flush=True)
            tts.speak(response)
            
        except KeyboardInterrupt:
            print("\n[Talk mode disabled]", flush=True)
            break
        except Exception as e:
            log_error(e, "talk_mode")
            print(f"Error: {e}", flush=True)


def main():
    load_config()
    
    personality = select_personality()
    system_prompt = get_personality_system_prompt(personality)
    voice = get_personality_voice(personality)
    print(f"Personality: {personality} | Voice: {voice}\n", flush=True)
    
    logger = init_logging(personality)
    
    config = {
        "personality": personality,
        "voice": voice,
        "ollama_url": get_ollama_url(),
        "model": get_default_model(),
        "log_file": str(get_log_file_path())
    }
    log_config(config)
    
    print("Ava - Personal Assistant", flush=True)
    print("Type 'exit' to quit, 'new' for new conversation, 'talk' for voice output mode\n", flush=True)
    
    storage = Storage()
    client = OllamaClient(system_prompt=system_prompt)
    
    conversation_id = storage.create_conversation()
    
    voice_active = False
    
    while True:
        try:
            if voice_active:
                break
            
            print("You: ", end="", flush=True)
            user_input = input().strip()
            
            if user_input.lower() == "exit":
                print("Goodbye!", flush=True)
                break
            
            if user_input.lower() == "new":
                conversation_id = storage.create_conversation()
                print("Started new conversation.\n", flush=True)
                continue
            
            if user_input.lower() == "voice":
                voice_mode(client, storage, conversation_id)
                continue
            
            if user_input.lower() == "talk":
                talk_mode(client, storage, conversation_id, voice)
                continue
            
            if not user_input:
                continue
            
            storage.add_message(conversation_id, "user", user_input)
            
            context = storage.get_conversation(conversation_id)
            response = client.generate(user_input, context)
            
            storage.add_message(conversation_id, "assistant", response)
            
            print(f"Ava: {response}\n", flush=True)
            
        except KeyboardInterrupt:
            print("\nGoodbye!", flush=True)
            break
        except Exception as e:
            log_error(e, "main_loop")
            print(f"Error: {e}\n", flush=True)


if __name__ == "__main__":
    main()
