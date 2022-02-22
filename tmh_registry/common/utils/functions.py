def get_text_choice_value_from_label(choices, label):
    return [
        choice[0] for choice in choices if choice[1].upper() == label.upper()
    ][0]
