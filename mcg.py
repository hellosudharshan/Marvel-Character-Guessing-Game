import streamlit as st
import random
import json
import asyncio
import aiohttp
import re

# A large list of Marvel characters with key attributes for the game logic.
# This makes the game more dynamic and interesting.
EASY_CHARACTERS = [
    {"name": "Iron Man", "is_hero": True, "is_female": False, "is_team_leader": True, "is_from_earth": True, "is_human": True},
    {"name": "Captain America", "is_hero": True, "is_female": False, "is_team_leader": True, "is_from_earth": True, "is_human": True},
    {"name": "Thor", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": False, "is_human": False},
    {"name": "Black Widow", "is_hero": True, "is_female": True, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Hulk", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Loki", "is_hero": False, "is_female": False, "is_team_leader": False, "is_from_earth": False, "is_human": False},
    {"name": "Spider-Man", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Thanos", "is_hero": False, "is_female": False, "is_team_leader": True, "is_from_earth": False, "is_human": False},
    {"name": "Captain Marvel", "is_hero": True, "is_female": True, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Doctor Strange", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
]

MEDIUM_CHARACTERS = EASY_CHARACTERS + [
    {"name": "Wolverine", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Black Panther", "is_hero": True, "is_female": False, "is_team_leader": True, "is_from_earth": True, "is_human": True},
    {"name": "Scarlet Witch", "is_hero": True, "is_female": True, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Deadpool", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Groot", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": False, "is_human": False},
    {"name": "Gamora", "is_hero": True, "is_female": True, "is_team_leader": False, "is_from_earth": False, "is_human": False},
    {"name": "Star-Lord", "is_hero": True, "is_female": False, "is_team_leader": True, "is_from_earth": True, "is_human": True},
    {"name": "Magneto", "is_hero": False, "is_female": False, "is_team_leader": True, "is_from_earth": True, "is_human": False},
    {"name": "Green Goblin", "is_hero": False, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "She-Hulk", "is_hero": True, "is_female": True, "is_team_leader": False, "is_from_earth": True, "is_human": True},
]

HARD_CHARACTERS = MEDIUM_CHARACTERS + [
    {"name": "Hela", "is_hero": False, "is_female": True, "is_team_leader": True, "is_from_earth": False, "is_human": False},
    {"name": "Doctor Doom", "is_hero": False, "is_female": False, "is_team_leader": True, "is_from_earth": True, "is_human": True},
    {"name": "Jessica Jones", "is_hero": True, "is_female": True, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Elektra", "is_hero": True, "is_female": True, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Jean Grey", "is_hero": True, "is_female": True, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Rocket Raccoon", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": False, "is_human": False},
    {"name": "Drax the Destroyer", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": False, "is_human": False},
    {"name": "Ant-Man", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Wasp", "is_hero": True, "is_female": True, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Falcon", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Winter Soldier", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Vision", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": False, "is_human": False},
    {"name": "Ultron", "is_hero": False, "is_female": False, "is_team_leader": True, "is_from_earth": False, "is_human": False},
    {"name": "Doctor Octopus", "is_hero": False, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Kingpin", "is_hero": False, "is_female": False, "is_team_leader": True, "is_from_earth": True, "is_human": True},
    {"name": "Daredevil", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Miles Morales", "is_hero": True, "is_female": False, "is_team_leader": False, "is_from_earth": True, "is_human": True},
    {"name": "Gwen Stacy (Spider-Gwen)", "is_hero": True, "is_female": True, "is_team_leader": False, "is_from_earth": True, "is_human": True},
]

DIFFICULTY_LEVELS = {
    "Easy": {"characters": EASY_CHARACTERS, "guesses": 10},
    "Medium": {"characters": MEDIUM_CHARACTERS, "guesses": 15},
    "Hard": {"characters": HARD_CHARACTERS, "guesses": 20},
}

# --- Initialize Session State for Game State and Page Navigation ---
if 'game_mode' not in st.session_state:
    st.session_state.game_mode = "home"

# Initialize state for the AI Guessing Game
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'ai_game_started' not in st.session_state:
    st.session_state.ai_game_started = False
if 'ai_guesses_made' not in st.session_state:
    st.session_state.ai_guesses_made = 0
if 'ai_guesser_name' not in st.session_state:
    st.session_state.ai_guesser_name = ""
if 'ai_won' not in st.session_state:
    st.session_state.ai_won = False
if 'ai_history' not in st.session_state:
    st.session_state.ai_history = []
if 'ai_last_guess' not in st.session_state:
    st.session_state.ai_last_guess = ""

# Initialize state for the Human Guessing Game
if 'human_game_started' not in st.session_state:
    st.session_state.human_game_started = False
if 'secret_character' not in st.session_state:
    st.session_state.secret_character = {}
if 'human_guess_history' not in st.session_state:
    st.session_state.human_guess_history = []
if 'human_won' not in st.session_state:
    st.session_state.human_won = False
if 'human_clues' not in st.session_state:
    st.session_state.human_clues = []
if 'human_guesses_made' not in st.session_state:
    st.session_state.human_guesses_made = 0
if 'human_question_history' not in st.session_state:
    st.session_state.human_question_history = []
if 'human_guess_limit' not in st.session_state:
    st.session_state.human_guess_limit = 20
if 'clues_unlocked' not in st.session_state:
    st.session_state.clues_unlocked = 0

# --- API Configuration ---
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

# --- Game Logic Functions ---
async def call_gemini_api(prompt):
    """
    Calls the Gemini API to get a response.
    Returns a dictionary with the API response or None on error.
    """
    api_key = st.session_state.api_key
    if not api_key:
        st.error("API key is not set. Please enter your API key on the home page.")
        return None

    headers = {'Content-Type': 'application/json'}
    payload = {'contents': [{'parts': [{'text': prompt}]}]}

    # Simple exponential backoff retry logic
    retries = 3
    delay = 1
    for i in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{API_URL}?key={api_key}", json=payload, headers=headers) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result
        except aiohttp.ClientError as e:
            st.error(f"API call failed: {e}. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
            delay *= 2
    return None

async def get_ai_question():
    """
    Generates the next question or guess from the AI using the Gemini API.
    """
    history_text = "\n".join([f"{item['role']}: {item['text']}" for item in st.session_state.ai_history])
    
    prompt = (
        "You are playing a '20 Questions' style game to guess a Marvel character. "
        "The user will only answer 'yes' or 'no'. Based on the conversation history below, "
        "ask your next yes/no question. "
        "If you are confident you know the character, make a final guess by starting your response with 'I guess: '."
        "Keep your questions concise. \n\n"
        "Conversation History:\n"
        f"{history_text}\n\n"
        "My next question is:"
    )
    
    response = await call_gemini_api(prompt)
    if response and 'candidates' in response and len(response['candidates']) > 0 and 'parts' in response['candidates'][0]['content']:
        return response['candidates'][0]['content']['parts'][0]['text'].strip()
    return "I'm having trouble thinking of a question. You win!"

async def get_human_clues(character_name):
    """
    Generates descriptive clues for the human player using the Gemini API.
    """
    prompt = (
        f"Generate 3 creative and descriptive clues for the Marvel character '{character_name}'. "
        "Each clue should be on a new line and should not contain the character's name. "
        "Do not use generic 'yes/no' questions. "
        "Example output:\n"
        "This character is known for their high-tech armored suit.\n"
        "They are the original leader of the Avengers.\n"
        "They are a billionaire genius inventor."
    )
    
    response = await call_gemini_api(prompt)
    if response and 'candidates' in response and len(response['candidates']) > 0 and 'parts' in response['candidates'][0]['content']:
        clues_text = response['candidates'][0]['content']['parts'][0]['text'].strip()
        return clues_text.split('\n')
    return ["I'm having trouble generating clues. You're on your own!"]
    
async def get_yes_no_response(question, character_name):
    """
    Gets a simple 'Yes' or 'No' answer from Gemini for a user's question.
    """
    prompt = (
        f"The secret Marvel character is '{character_name}'. "
        f"Answer the following question with only 'Yes' or 'No'. "
        f"Do not provide any other information. "
        f"Question: {question}"
    )
    response = await call_gemini_api(prompt)
    if response and 'candidates' in response and len(response['candidates']) > 0 and 'parts' in response['candidates'][0]['content']:
        answer = response['candidates'][0]['content']['parts'][0]['text'].strip().lower()
        if 'yes' in answer:
            return "Yes. 👍"
        elif 'no' in answer:
            return "No. 👎"
    return "I can't answer that question right now."

async def handle_human_question():
    """
    Handles the human player's question, gets an answer from the AI,
    and updates the conversation history.
    """
    question = st.session_state.human_question_input.strip()

    if not question:
        st.warning("Please enter a question.")
        return

    st.session_state.human_guesses_made += 1
    
    # Get the AI's answer
    answer = await get_yes_no_response(question, st.session_state.secret_character["name"])
    
    # Append to the conversation history
    st.session_state.human_question_history.append(f"You: {question}")
    st.session_state.human_question_history.append(f"AI: {answer}")

    # Clear the input box
    st.session_state.human_question_input = ""
    st.rerun()

def start_ai_game_mode():
    """Sets the game mode to 'ai_guesses' and initializes the game."""
    st.session_state.game_mode = "ai_guesses"
    st.session_state.ai_game_started = False
    st.session_state.ai_guesses_made = 0
    st.session_state.ai_won = False
    st.session_state.ai_history = []
    st.session_state.ai_last_guess = ""

def start_human_game_mode():
    """Sets the game mode to 'human_guesses' and initializes the game."""
    st.session_state.game_mode = "human_guesses"
    st.session_state.human_game_started = True
    
    # Select character list and guess limit based on difficulty
    difficulty_data = DIFFICULTY_LEVELS[st.session_state.difficulty]
    character_list = difficulty_data["characters"]
    st.session_state.human_guess_limit = difficulty_data["guesses"]
    st.session_state.secret_character = random.choice(character_list)
    
    st.session_state.human_guess_history = []
    st.session_state.human_won = False
    st.session_state.human_clues = [] # Reset clues
    st.session_state.human_guesses_made = 0 # Reset guess counter
    st.session_state.human_question_history = [] # Reset question history
    st.session_state.clues_unlocked = 0 # Reset unlocked clues
    
def go_home():
    """Resets the game mode to 'home' to return to the main menu."""
    st.session_state.game_mode = "home"
    st.session_state.ai_game_started = False
    st.session_state.human_game_started = False

def start_ai_round():
    """Starts the AI's guessing round after the character name is entered."""
    if st.session_state.character_for_ai:
        st.session_state.ai_guesser_name = st.session_state.character_for_ai.strip()
        st.session_state.ai_game_started = True
        st.rerun()
    else:
        st.error("Please enter a character name to start the game.")

async def handle_ai_response(response):
    """
    Handles the user's 'yes/no' response to the AI's question and gets the next question.
    """
    st.session_state.ai_guesses_made += 1
    
    # Append the user's answer to the chat history
    st.session_state.ai_history.append({'role': 'user', 'text': response})
    
    # Generate the next AI question/guess
    st.session_state.ai_last_guess = "" # Reset previous guess
    question_or_guess = await get_ai_question()
    st.session_state.ai_history.append({'role': 'model', 'text': question_or_guess})
    
    if question_or_guess.lower().startswith('i guess:'):
        final_guess = question_or_guess.split(':', 1)[1].strip()
        st.session_state.ai_last_guess = final_guess
        if final_guess.lower() == st.session_state.ai_guesser_name.lower():
            st.session_state.ai_won = True
            st.success(f"I got it! Your character is... {final_guess}! 🎉")
            st.balloons()
        else:
            st.error(f"Hmm, my final guess is **{final_guess}**, but that's not right. You win! �")
    
    st.rerun()

def handle_human_guess():
    """Handles the human's guess, checking if it's correct."""
    guess = st.session_state.human_guess_input.strip()
    
    if not guess:
        st.error("Please enter a guess before submitting.")
        return

    st.session_state.human_guesses_made += 1

    # Normalize the guess and the secret character's name
    normalized_guess = re.sub(r'[\s-]', '', guess).lower()
    normalized_secret_name = re.sub(r'[\s-]', '', st.session_state.secret_character["name"]).lower()

    if normalized_guess == normalized_secret_name:
        st.session_state.human_won = True
        st.balloons()
        st.success(f"You got it! The character was **{st.session_state.secret_character['name']}**! 🎉")
    else:
        st.error("That's not it! 😞 Keep trying.")

def get_clue():
    """Deduct guesses and reveal a clue."""
    if st.session_state.clues_unlocked < len(st.session_state.human_clues):
        # A clue costs 3 guesses
        clue_cost = 3
        st.session_state.human_guesses_made += clue_cost
        st.session_state.human_question_history.append(f"**-- CLUE UNLOCKED ({clue_cost} GUESSES DEDUCTED) --**")
        st.session_state.human_question_history.append(f"💡 **Clue {st.session_state.clues_unlocked + 1}:** {st.session_state.human_clues[st.session_state.clues_unlocked]}")
        st.session_state.clues_unlocked += 1
    else:
        st.warning("You have unlocked all available clues!")
    st.rerun()

# --- UI Layout based on game_mode ---

if st.session_state.game_mode == "home":
    st.title("Welcome to the Marvel Character Guessing Game! 💥")
    st.markdown("Please enter your Gemini API key to begin.")
    st.text_input("Enter your API key:", type="password", key="api_key_input", on_change=lambda: st.session_state.update(api_key=st.session_state.api_key_input))
    
    if st.session_state.api_key:
        st.markdown("---")
        st.markdown("Choose a game mode below to start playing.")
        
        # New difficulty selection
        st.session_state.difficulty = st.selectbox(
            "Select Difficulty:",
            list(DIFFICULTY_LEVELS.keys()),
            key="difficulty_selector"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("You Make the Guess", on_click=start_human_game_mode, use_container_width=True)
        with col2:
            st.button("I Find the Character", on_click=start_ai_game_mode, use_container_width=True)

elif st.session_state.game_mode == "human_guesses":
    st.title("You Are the Guesser")
    st.button("Back to Main Menu", on_click=go_home, use_container_width=True)
    st.markdown("---")

    if st.session_state.human_won:
        st.success(f"You got it! The character was **{st.session_state.secret_character['name']}**! 🎉")
        st.button("Play Again", on_click=start_human_game_mode, use_container_width=True)
    elif st.session_state.human_guesses_made >= st.session_state.human_guess_limit:
        st.error(f"You've run out of guesses! The character was **{st.session_state.secret_character['name']}**.")
        st.button("Play Again", on_click=start_human_game_mode, use_container_width=True)
    else:
        st.subheader("Instructions:")
        st.write("I've thought of a character. Ask me questions, and I will answer with 'Yes' or 'No'. You can guess at any time!")
        st.info(f"Guesses left: {st.session_state.human_guess_limit - st.session_state.human_guesses_made}")
        
        # Call the Gemini API to get clues if they don't exist yet
        if not st.session_state.human_clues:
            with st.spinner("Preparing the game..."):
                clues = asyncio.run(get_human_clues(st.session_state.secret_character["name"]))
                st.session_state.human_clues = clues
                st.rerun()

        # Add "Get Clue" button
        st.button("Get a Clue (Costs 3 Guesses)", on_click=get_clue, disabled=st.session_state.clues_unlocked >= len(st.session_state.human_clues))

        st.text_input("Ask a question:", key="human_question_input", on_change=lambda: asyncio.run(handle_human_question()))
        
        # Use a form to group the guess input and button for automatic resetting
        with st.form("human_guess_form"):
            st.text_input("Enter your final guess:", key="human_guess_input")
            if st.form_submit_button("Submit Guess", use_container_width=True):
                handle_human_guess()
        
        st.markdown("---")
        st.subheader("Conversation History")
        for line in st.session_state.human_question_history:
            st.write(line)
        
elif st.session_state.game_mode == "ai_guesses":
    st.title("I Am the Guesser")
    st.button("Back to Main Menu", on_click=go_home, use_container_width=True)
    st.markdown("---")
    
    if not st.session_state.ai_game_started:
        st.write("Think of a Marvel character and enter their name below. I'll ask questions to try and guess it!")
        st.text_input("Enter your character's name:", key="character_for_ai", placeholder="e.g., Captain Marvel")
        if st.button("Start Game", on_click=start_ai_round):
            pass
    else:
        if st.session_state.ai_last_guess:
            st.write(f"My last guess was: **{st.session_state.ai_last_guess}**")
        
        if not st.session_state.ai_won and not st.session_state.ai_last_guess:
            if st.session_state.ai_history and st.session_state.ai_history[-1]['role'] == 'model':
                current_question = st.session_state.ai_history[-1]['text']
                st.write(f"**My question:** {current_question}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes", key="ai_yes", use_container_width=True):
                        asyncio.run(handle_ai_response("yes"))
                with col2:
                    if st.button("No", key="ai_no", use_container_width=True):
                        asyncio.run(handle_ai_response("no"))
            else:
                st.write("Thinking of a question...")
                with st.spinner("I'm thinking..."):
                    asyncio.run(handle_ai_response("start"))
        
        if st.session_state.ai_won:
            st.success("I won this round! You can go back to the menu to play again.")
            st.button("Play Again", on_click=start_ai_game_mode, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Conversation History")
        for chat in st.session_state.ai_history:
            if chat['role'] == 'model':
                st.info(f"AI: {chat['text']}")
            else:
                st.write(f"You: {chat['text']}")
