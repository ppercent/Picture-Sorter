def get_widget_screen_position(widget):
    widget.update()

    x_relative = widget.winfo_x()
    y_relative = widget.winfo_y()
    x_window = widget.winfo_toplevel().winfo_x()
    y_window = widget.winfo_toplevel().winfo_y()
    x_screen = x_window + x_relative
    y_screen = y_window + y_relative

    return x_screen, y_screen

def get_wraplength(master, widget):
    pady = 50
    return master.winfo_screenwidth() - get_widget_screen_position(widget)[0] - pady

def is_sorting_valid(sorting_type):
    valid_separators = ['-', '_', '/', ' ']
    valid_chars = ['y', 'm', 'd']

    if sorting_type[0] == '/' or sorting_type[-1] == '/':
        # nameless folder to be created, invalid
        return False
    i = 0
    while i < len(sorting_type):
        char = sorting_type[i]
        if char in valid_separators:
            if char == '/':
                # subfolder, checking if folder name is supported
                try:
                    next_folder_index = sorting_type.index('/', i+1)
                    y = next_folder_index - 1
                    is_valid = False
                    while y > i:
                        if sorting_type[y] != ' ':
                            is_valid = True
                            break
                        y -= 1
                    if is_valid:
                        is_valid = False
                        i += 1
                        continue
                    else:
                        # only spaces in the folder name (blank name folder), invalid
                        return False

                except ValueError:
                    is_valid = False
                    for y in range(i+1, len(sorting_type)):
                        if sorting_type[y] != ' ':
                            is_valid = True
                            break
                    if is_valid:
                        is_valid = False
                        i += 1
                        continue
                    else:
                        # only spaces in the folder name (blank name folder), invalid
                        return False
            # is valid separator, skip to next char
            i+=1
            continue
        if char not in valid_chars and char not in valid_separators:
            # unsupported char, invalid
            return False
        if char == 'y':
            if len(sorting_type) - i < 4:
                # not enought place to fit 4 Ys, invalid
                return False
            else:
                for j in range(1, 4):
                    if sorting_type[i+j] != 'y':
                        # wrong Ys sequence, invalid
                        return False
                i += 4
                continue
        else:
            if len(sorting_type) - i < 2:
                # not enought place to fit 2 correct letters, invalid
                return False
            else:
                if char != sorting_type[i+1]:
                    # wrong sequence, invalid
                    return False
                i += 2
                continue
        i+=1
    # is valid
    return True

def is_naming_valid(naming_type):
    valid_separators = ['-', '_', ' ']
    valid_chars = ['y', 'm', 'd', 'H', 'M', 'S']

    i = 0
    while i < len(naming_type):
        char = naming_type[i]
        if char in valid_separators:
            # is valid separator, skip to next char
            i += 1
            continue
        if char not in valid_chars and char not in valid_separators:
            # unsupported char, invalid
            return False
        if char == 'y':
           if len(naming_type) - i < 4:
               # not enought place to fit 4 Ys, invalid
               return False
           else:
               for j in range(1, 4):
                   if naming_type[i+j] != 'y':
                       # wrong Ys sequence, invalid
                       return False
               i += 4
               continue
        else:
            if len(naming_type) - i < 2:
                # not enought place to fit 2 correct letters, invalid
                return False
            else:
                if naming_type[i] != naming_type[i+1]:
                    # wrong sequence, invalid
                    return False
                i += 2
                continue
        i += 1
    # is valid
    return True
