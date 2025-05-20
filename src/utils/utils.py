import re


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

def is_directory_field_valid(sorting_type):
    '''returns true if sorting type pathing is valid, false otherwise | ex. "/hey/bro -> invalid && hey/bro -> valid" '''
    
    elements = sorting_type.split('/')
    for elm in elements:
        if not elm.strip():
            return False
    return True

def is_date_item_valid(date_item):
    '''returns true if date item is valid, false otherwise | ex. "month", "day month year" '''
    
    if not date_item:
        return False
        
    valid_date_items = set(['second', 'minute', 'hour', 'day', 'month', 'year'])
    parsed = set(date_item.split())

    return len(parsed & valid_date_items) == len(parsed)


def is_field_type_valid(field, is_naming_type=0):
    '''returns true if sorting type is valid, false otherwise | ex. "my sorted pictures (<year months>)" '''

    exclusion_chars = r'/\:?"|<>' if is_naming_type else r'\:?"|<>'
    date_pattern = r'<([a-zA-Z ]*)>'
    date_replacement = r'\1'
    parsed = re.sub(date_pattern, date_replacement, field)

    # invalid characters for file naming conventions
    if set(exclusion_chars) & set(parsed):
        return False
    
    # check if date items are invalid
    date_items = re.findall(date_pattern, field)
    for date_item in date_items:
        if not is_date_item_valid(date_item):
            return False
            
    # makes sure the directories are valid (only for sorting_type)
    if not is_naming_type and not is_directory_field_valid(field):
        return False
        
    return True
