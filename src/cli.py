import sys
from src.core.config import load_config, get_available_personalities, get_default_personality, get_personality_system_prompt
from src.core.llm import OllamaClient
from src.core.storage import Storage


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


def main():
    load_config()
    
    print("Ava - Personal Assistant", flush=True)
    print("Type 'exit' to quit, 'new' for new conversation\n", flush=True)
    
    personality = select_personality()
    system_prompt = get_personality_system_prompt(personality)
    print(f"Personality: {personality}\n", flush=True)
    
    storage = Storage()
    client = OllamaClient(system_prompt=system_prompt)
    
    conversation_id = storage.create_conversation()
    
    while True:
        try:
            print("You: ", end="", flush=True)
            user_input = input().strip()
            # user_input = input("You: ", flush=True).strip()
            
            if user_input.lower() == "exit":
                print("Goodbye!", flush=True)
                break
            
            if user_input.lower() == "new":
                conversation_id = storage.create_conversation()
                print("Started new conversation.\n", flush=True)
                continue
            
            if not user_input:
                continue
            
            storage.add_message(conversation_id, "user", user_input)
            
            context = storage.get_conversation(conversation_id)
            response = client.generate(user_input, context)
            
            storage.add_message(conversation_id, "assistant", response)
            
            print(f"Ava: {response}\n", flush=True)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n", flush=True)


if __name__ == "__main__":
    main()
