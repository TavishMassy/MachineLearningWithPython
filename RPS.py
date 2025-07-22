import random
from collections import Counter

# Global variables
my_history = []
opponent_history = []
game_count = 0

def player(prev_play, opponent_history_param=[]):
    global my_history, opponent_history, game_count
    
    # Initialize on first play
    if prev_play == "":
        my_history = []
        opponent_history = []
        game_count = 0
        return "R"
    
    # Update histories
    opponent_history.append(prev_play)
    game_count += 1
    
    # Strategy 1: Counter Quincy's fixed pattern
    if detect_quincy():
        quincy_counter = ["P", "P", "S", "S", "R"]
        pattern_index = game_count % 5
        guess = quincy_counter[pattern_index]
        my_history.append(guess)
        return guess
    
    # Strategy 2: Counter Kris (plays counter to our previous move)
    if detect_kris():
        if len(my_history) > 0:
            my_last = my_history[-1]
            kris_response = get_counter(my_last)
            guess = get_counter(kris_response)
        else:
            guess = "P"
        my_history.append(guess)
        return guess
    
    # Strategy 3: Counter Mrugesh (counters our most frequent move in last 10)
    if detect_mrugesh():
        if len(my_history) >= 3:
            recent_my_moves = my_history[-10:]
            move_counts = Counter(recent_my_moves)
            my_most_frequent = move_counts.most_common(1)[0][0]
            mrugesh_response = get_counter(my_most_frequent)
            guess = get_counter(mrugesh_response)
        else:
            guess = "S"
        my_history.append(guess)
        return guess
    
    # Strategy 4: Counter Abbey (uses pair-based sequence prediction)
    # Abbey is tricky - let's assume it's Abbey if not others
    if len(opponent_history) >= 3:
        guess = anti_abbey_strategy()
        my_history.append(guess)
        return guess
    
    # Default early game strategy
    guess = "R"
    my_history.append(guess)
    return guess

def detect_quincy():
    """Detect Quincy's R-R-P-P-S pattern"""
    if len(opponent_history) < 5:
        return False
    
    # Check for exact pattern match
    quincy_pattern = ["R", "R", "P", "P", "S"]
    
    # Check if recent moves match the pattern
    for offset in range(5):
        match = True
        for i in range(min(5, len(opponent_history))):
            expected = quincy_pattern[(i + offset) % 5]
            if opponent_history[-(5-i)] != expected:
                match = False
                break
        if match:
            return True
    
    return False

def detect_kris():
    """Detect Kris strategy - counters our previous move"""
    if len(opponent_history) < 3 or len(my_history) < 3:
        return False
    
    matches = 0
    for i in range(min(4, len(my_history)-1)):
        if len(opponent_history) > i:
            expected = get_counter(my_history[-(i+2)])
            if opponent_history[-(i+1)] == expected:
                matches += 1
    
    return matches >= 3

def detect_mrugesh():
    """Detect Mrugesh strategy - counters our most frequent recent move"""
    if len(opponent_history) < 3 or len(my_history) < 5:
        return False
    
    matches = 0
    for i in range(min(3, len(my_history)-3)):
        check_history = my_history[-(10+i):-(i)] if i > 0 else my_history[-10:]
        if len(check_history) >= 3:
            move_counts = Counter(check_history)
            most_frequent = move_counts.most_common(1)[0][0]
            expected = get_counter(most_frequent)
            if len(opponent_history) > i and opponent_history[-(i+1)] == expected:
                matches += 1
    
    return matches >= 2

def anti_abbey_strategy():
    """Counter Abbey's exact algorithm"""
    # Abbey's actual algorithm (from the code):
    # 1. She tracks ALL pairs of consecutive moves we make in play_order dict
    # 2. She looks at our previous move (prev_opponent_play)
    # 3. She creates 3 potential plays: prev_play+"R", prev_play+"P", prev_play+"S"
    # 4. She finds which of these 3 pairs has the highest count in her history
    # 5. She predicts we'll play the second letter of the most frequent pair
    # 6. She plays the counter to that prediction
    
    if len(my_history) < 1:
        return "R"
    
    # Get what Abbey sees as our "previous move" (our last move)
    prev_move = my_history[-1]
    
    # Simulate Abbey's pair tracking
    # She tracks pairs of consecutive moves we've made
    pair_counts = {}
    
    # Build the history of pairs Abbey has seen
    for i in range(len(my_history) - 1):
        pair = my_history[i] + my_history[i + 1]
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
    
    # Abbey creates potential plays based on our last move
    potential_plays = [
        prev_move + "R",
        prev_move + "P", 
        prev_move + "S"
    ]
    
    # Find which potential play has highest count
    max_count = -1
    abbey_prediction = "R"  # default
    
    for play in potential_plays:
        count = pair_counts.get(play, 0)
        if count > max_count:
            max_count = count
            abbey_prediction = play[-1]  # last character of the pair
    
    # Abbey will play the counter to her prediction
    abbey_move = get_counter(abbey_prediction)
    
    # We play the counter to Abbey's move
    our_move = get_counter(abbey_move)
    
    # However, if we don't have enough history, Abbey might be unpredictable
    # Use a strategy that creates confusing patterns for her algorithm
    if len(my_history) < 5:
        # Early game: create pairs that will confuse her later
        confusion_sequence = ["R", "P", "S", "R", "S", "P", "R", "S", "P", "S"]
        return confusion_sequence[len(my_history) % len(confusion_sequence)]
    
    # If all pairs have equal count (0), Abbey will default to the first option
    if max_count == 0:
        # Abbey will predict "R" (first option), so counter that
        return get_counter(get_counter("R"))
    
    return our_move

def get_counter(move):
    """Returns the move that beats the given move"""
    counters = {'R': 'P', 'P': 'S', 'S': 'R'}
    return counters[move]