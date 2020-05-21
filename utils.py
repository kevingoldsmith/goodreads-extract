import readline

def get_interactive_history():
    print('\n'.join([str(readline.get_history_item(i + 1)) for i in range(readline.get_current_history_length())]))
