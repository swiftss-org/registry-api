def get_text_choice_value_from_label(choices, label):
    values = [choice[0] for choice in choices if choice[1].upper() == label.upper()]
    if len(values) == 0:
        raise IndexError('Unable to find label "{}" in choices "{}"'.format(label, choices))

    return values[0]
