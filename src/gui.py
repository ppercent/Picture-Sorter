import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
from customtkinter import CTkEntry, CTkButton, CTkFrame
from utils.tooltip import CustomTooltipLabel
from utils import utils
from file_operation.file_utils import FileUtils, get_folder

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Trieur D\'images')
        self.geometry('833x670+89+64')
        self.resizable(False, False)
        self.configure(bg='#323232')
        self.init_variables()
        self.init_images()

        # delete here
        self.bind('<Motion>', self.update_title)
        self.mouse_pos_text = tk.StringVar()
        self.mouse_pos_text.set('(0, 0)')

    def init_variables(self):
        # checkboxes
        self.filetype_check_var = tk.StringVar(value='off')
        self.insertname_check_var = tk.StringVar(value='off')

        # entries
        self.path_entry_var = tk.StringVar(value='')
        self.output_path_var = tk.StringVar(value='')
        self.namingtype_entry_var = tk.StringVar(value='')
        self.sortingtype_entry_var = tk.StringVar(value='')

        # global button state
        self.button_state = ['1', '1', '1', '1'] # 0: invalid, red | 1: neutral, grey | 2: valid, green

        # folder
        self.folder = None


    def init_images(self):
        self.yes_image = tk.PhotoImage(file=os.getcwd() + '\\src\\assets\\oui_64px.png')
        self.no_image = tk.PhotoImage(file=os.getcwd() + '\\src\\assets\\non_64px.png')
        self.tip_image = tk.PhotoImage(file=os.getcwd() + '\\src\\assets\\info_25px.png')

    def toggle_button_state(self, state):
        self.yes_to_all_button.configure(state=tk.NORMAL if state == 'normal' else tk.DISABLED)
        self.no_to_all_button.configure(state=tk.NORMAL if state == 'normal' else tk.DISABLED)
        self.yes_button.configure(state=tk.NORMAL if state == 'normal' else tk.DISABLED)
        self.no_button.configure(state=tk.NORMAL if state == 'normal' else tk.DISABLED)

        if state == 'normal':
            self.hide_buttons_frame.place_forget()
        else:
            self.hide_buttons_frame.place(x=550, y=213)

    def browse_file(self, text_variable, *args):
        path = filedialog.askdirectory(mustexist=False, initialdir=os.getcwd())

        if path:
            text_variable.set(path)

    def button_start_on_click(self):
        try:
            self.folder = get_folder(self.button_state)
        except ValueError as e:
            print(e) # update gui as error with e

    def update_title(self, event): # delete here
        self.title_text = f'Trieur D\'images - x={event.x} y={event.y}'
        self.title(self.title_text)
        self.mouse_pos_text.set(f'({event.x}, {event.y})')

    def update_entries(self):
        # possible_state = ['2222', '2122', '2212', '2221', '2112', '2121']
        # impossible_state = [0xxx, 1xxx, 1x11, 2x11, 2x00]
        entries = [self.path_entry, self.output_path, self.sortingtype_entry, self.namingtype_entry]
        joined = ''.join(self.button_state)
        print(joined)
        for i in range(4):
            current_entry = entries[i]
            current_state = int(joined[i])
            if current_state == 0:
                print('set color to red')
                current_entry.configure(border_color=self.border_color_invalid)
            elif current_state == 1:
                current_entry.configure(border_color=self.border_color)
            else:
                current_entry.configure(border_color=self.border_color_valid)

    def update_button_state(self, field_index, value):
        '''update the global button state, field_index is the index between 1-4'''
        self.button_state[field_index-1] = value
        self.update_entries()

    def add_line(text): # TODO STOPPED HERE TO BE CONTINUED

    def update_gui_fields(self, field_index, *args):
        print('called ->', field_index)
        if field_index == 1:
            # is path entry
            if len(self.path_entry_var.get()) == 0:
                # is neutral
                print('is neutral')
                self.update_button_state(field_index, '1')
                return
            if FileUtils.directoryExists(bytes(self.path_entry_var.get(), 'utf-8')):
                # is valid
                print('is valid')
                self.update_button_state(field_index, '2')
            else:
                # is invalid
                print('is invalid')
                self.update_button_state(field_index, '0')

        elif field_index == 2:
            # is output path
            if len(self.output_path_var.get()) == 0:
                # is neutral
                self.update_button_state(field_index, '1')
                return
            if FileUtils.directoryExists(bytes(self.output_path_var.get(), 'utf-8')):
                # is valid
                self.update_button_state(field_index, '2')
            else:
                # is invalid
                self.update_button_state(field_index, '0')

        elif field_index == 3:
            if len(self.sortingtype_entry_var.get()) == 0:
                # is neutral
                self.update_button_state(field_index, '1')
                return
            if utils.is_sorting_valid(self.sortingtype_entry_var.get()):
                # is valid
                self.update_button_state(field_index, '2')
            else:
                # is invalid
                self.update_button_state(field_index, '0')
        else:
            if len(self.namingtype_entry_var.get()) == 0:
                # is neutral
                self.update_button_state(field_index, '1')
                return
            if utils.is_naming_valid(self.namingtype_entry_var.get()):
                # is valid
                self.update_button_state(field_index, '2')
            else:
                # is invalid
                self.update_button_state(field_index, '0')

    def draw_gui(self):
        # texts
        self.title_text = 'Trieur D\'images - Developpé Par Constantin™ ;)'
        explaination_text = 'Ce programme permet de trier et nommer par date des photos et des documents en masse.'
        example_text = (
            "       Pour un mode de triage: yyyy/yyyymm et de nommage yyyymmddhhMMss, l'arborescence serai la suivante:\n"
            "                 2024/\n"
            "                 └── 2024 01/\n"
            "                     ├── 2024-01-17-10-29-05.jpg\n"
            "                     └── 2024-01-21-14-45-32.jpg\n"
            "\n"
            "                 2023/\n"
            "                 └── 2023 12/\n"
            "                     ├── 2023-12-10-19-03-10.jpg\n"
            "                     └── 2023-12-16-22-38-45.jpg\n")
        path_entry_text = '1. Entrez le repertoire de photos:'
        output_path_text = '2. Entrez le repertoire de sortie'
        sortingtype_text = '3. Entrez le mode de triage:'
        namingtype_text = '4. Entrez le mode de renommage'
        path_entry_tip_text = "Chemin d'accès du dossier contenant les photos/vidéos/documents à trier"
        output_path_tip_text = "Destination du tri. Si vide, trie dans le dossier d'origine"
        sortingtype_tip_text = (
            "Format de tri des dossiers: '/' pour créer un sous-dossier, 'yyyy' (année), 'mm' (mois), 'dd' (jour) pour nommer les dossiers. \n"
            "Il est possible d'espacer les éléments de date avec: '-', '_', ' ' \n\n"
            "Ex: 'yyyy/yyyy-mm' donne :\n"
            ".\n"
            "└── repertoire_sortie/\n"
            "    ├── 2024/\n"
            "    │   └── 2024-01/\n"
            "    │       ├── IMG_20240117_102905.jpg\n"
            "    │       └── IMG_20240121_144532.jpg\n"
            "    └── 2023/\n"
            "        └── 2023-12/\n"
            "            ├── IMG_20231210_190310.jpg\n"
            "            └── IMG_20231216_223845.jpg\n"
            "\n(Vide = pas de tri)")
        namingtype_tip_text = (
            "Format de renommage des fichiers : \n"
            "'yyyy' (année), 'mm' (mois), 'dd' (jour), 'HH' (heure), 'MM' (minute), 'SS' (seconde). \n"
            "Il est possible d'espacer les éléments de date avec: '-', '_', ' ' \n\n"
            "Ex: 'yyyy-mm-dd' renomme en '2024-03-15'. \n"
            "\n(Vide = pas de renommage)")
        additional_tip = "Au moins une option (tri ou renommage) doit être sélectionnée pour que le programme fonctionne"
        option_text = 'Options supplémentaires:'
        # filetype_check_text = 'Tri uniquement les photos/vidéos (Si un document est trouvé, on peut choisir de le trier ou non.)'
        filetype_check_text = 'Trie également les documents, en plus des photos/vidéos (on peut choisir de le trier ou non.)'

        # insertname_check_text = 'Ajoute la date à la fin du nom du fichier au le de le remplacer (requier l\'utilisation d\'un mode de renommage)'
        insertname_check_text = 'Remplace entièrement le nom du fichier par sa date (requier l\'utilisation d\'un mode de renommage)'

        # WIDGETS

        # styling
        default_font = ('SF Pro', 12)
        caption_font = ('SF Pro', 12, 'bold')
        tip_font = ('Consolas', 11)
        background_color = '#323232'
        text_color = '#e5e5e6'
        self.border_color = '#565656'
        self.border_color_invalid = '#920101'
        self.border_color_valid = '#AAD1A7'
        field_foreground_color = '#434343'
        button_background_color = '#5a565f'
        button_background_hover_color = '#79737F'
        ttk_styling = ttk.Style()
        ttk_styling.configure('BlackFrame.TFrame', background=background_color)
        ttk_styling.configure('BlackCheckbutton.TCheckbutton', foreground=text_color, font=default_font, background=background_color)

        # explaination text
        explaination_frame = ttk.Frame(self, style='BlackFrame.TFrame')

        title_label = ttk.Label(self, text=self.title_text, foreground=text_color, background=background_color, font=default_font)
        explaination_label = ttk.Label(explaination_frame, text=explaination_text, foreground=text_color, background=background_color, font=caption_font)
        example_label = ttk.Label(explaination_frame, text=example_text, foreground=text_color, background=background_color, font=default_font)

        # explaination text layout
        title_label.pack(pady=15)
        explaination_label.pack(pady=8)
        # example_label.pack()
        explaination_frame.pack(side='left', anchor='nw')

        # path entry
        path_entry_frame = ttk.Frame(self, style='BlackFrame.TFrame')
        path_entry_label = ttk.Label(self, text=path_entry_text, font=caption_font,
                             foreground=text_color, background=background_color)
        self.path_entry = CTkEntry(path_entry_frame, height=25, width=450, border_width=1,
                              border_color=self.border_color, bg_color=background_color,
                              placeholder_text=r'C:\Users\YourUsername\Documents\InputFolder', textvariable=self.path_entry_var,
                              fg_color=field_foreground_color, text_color=text_color, corner_radius=3)
        browse_path_button = CTkButton(path_entry_frame, text='...', height=25, width=25,
                                       bg_color=background_color, fg_color=button_background_color,
                                       corner_radius=3, hover_color=button_background_hover_color,
                                       command=lambda: self.browse_file(self.path_entry_var))
        
        # entry fields layout
        self.path_entry.pack(side='left', anchor='nw')
        browse_path_button.pack(padx=12, side='left', anchor='ne')
        path_entry_label.place(x=20, y=120) #+25 next 300 before
        path_entry_frame.place(x=15, y=145) #+55 next 325 before | +35 (-20)

        # output path
        output_path_frame = ttk.Frame(self, style='BlackFrame.TFrame')
        output_path_label = ttk.Label(self, text=output_path_text, font=caption_font, foreground=text_color, background=background_color)
        self.output_path = CTkEntry(output_path_frame, height=25, width=450, border_width=1,
                              border_color=self.border_color, bg_color=background_color, textvariable=self.output_path_var,
                              placeholder_text='laisser vide pour trier dans le dossier du repertoir photo',
                              fg_color=field_foreground_color, text_color=text_color, corner_radius=3)
        browse_path_button_2 = CTkButton(output_path_frame, text='...', height=25, width=25,
                                       bg_color=background_color, fg_color=button_background_color,
                                       corner_radius=3, hover_color=button_background_hover_color,
                                       command=lambda: self.browse_file(self.output_path_var))
        
        self.output_path.pack(side='left', anchor='nw')
        browse_path_button_2.pack(padx=12, side='left', anchor='ne')
        output_path_label.place(x=20, y=180) #+25 next
        output_path_frame.place(x=15, y=205) #+55 next


        # sorting type
        sortingtype_frame = ttk.Frame(self, style='BlackFrame.TFrame')
        sortingtype_label = ttk.Label(self, text=sortingtype_text, font=caption_font,
                             foreground=text_color, background=background_color)
        self.sortingtype_entry = CTkEntry(sortingtype_frame, height=25, width=450, border_width=1, textvariable=self.sortingtype_entry_var,
                              border_color=self.border_color, bg_color=background_color, placeholder_text='yyyy/mm/dd',
                              fg_color=field_foreground_color, text_color=text_color,
                              corner_radius=3)
        sortingtype_button_tip = tk.Button(sortingtype_frame, relief='flat', bd=0, activebackground=background_color, background=background_color, image=self.tip_image)

        sortingtype_label.place(x=20, y=380-180-20+55)
        self.sortingtype_entry.pack(side='left', anchor='nw')
        sortingtype_button_tip.pack(padx=12, side='left', anchor='ne')
        sortingtype_frame.place(x=15, y=405-180-20+55)

        sortingtype_tip = CustomTooltipLabel(anchor_widget=sortingtype_button_tip, text=sortingtype_tip_text,
                           background='#2c2c2c', font=tip_font,
                           wraplength=utils.get_wraplength(self, sortingtype_button_tip),
                           foreground=text_color, hover_delay=500, border=1)


        # naming type
        namingtype_frame = ttk.Frame(self, style='BlackFrame.TFrame')
        namingtype_label = ttk.Label(self, text=namingtype_text, font=caption_font,
                             foreground=text_color, background=background_color)
        self.namingtype_entry = CTkEntry(namingtype_frame, height=25, width=450, border_width=1,
                              border_color=self.border_color, bg_color=background_color, textvariable=self.namingtype_entry_var,
                              fg_color=field_foreground_color, text_color=text_color,
                              corner_radius=3, placeholder_text='laisser vide pour ne pas renomer')
        namingtype_button_tip = tk.Button(namingtype_frame, relief='flat', bd=0, activebackground=background_color, background=background_color, image=self.tip_image)

        namingtype_label.place(x=20, y=260+35)
        self.namingtype_entry.pack(side='left', anchor='nw')
        namingtype_button_tip.pack(padx=12, side='left', anchor='ne')
        namingtype_frame.place(x=15, y=260+25+35)

        namingtype_tip = CustomTooltipLabel(anchor_widget=namingtype_button_tip, text=namingtype_tip_text,
                           background='#2c2c2c', font=tip_font,
                           wraplength=utils.get_wraplength(self, namingtype_button_tip),
                           foreground=text_color, hover_delay=500, border=1)

        # advanced options
        option_text_label = ttk.Label(self, text=option_text, font=caption_font,
                             foreground=text_color, background=background_color)
        filetype_check = ttk.Checkbutton(self, text=filetype_check_text, takefocus=False,
                                         style='BlackCheckbutton.TCheckbutton', variable=self.filetype_check_var,
                                         onvalue='on', offvalue='off')
        insertname_check = ttk.Checkbutton(self, text=insertname_check_text, takefocus=False,
                                           style='BlackCheckbutton.TCheckbutton', variable=self.insertname_check_var,
                                           onvalue='on', offvalue='off')
        additional_tip_label = ttk.Label(self, text=additional_tip, font=('Monaco', 10),
                             foreground=text_color, background=background_color, wraplength=505)


        option_text_label.place(x=20, y=410-30)
        filetype_check.place(x=30, y=445-30-7)
        insertname_check.place(x=30, y=470-30-7)
        additional_tip_label.place(x=5, y=345)

        # buttons
        button_frame = CTkFrame(self, height=270, width=170, corner_radius=10, fg_color='#3D3D3D', border_width=1, border_color='#3D3D3D')
        border_frame = CTkFrame(self, height=8, width=170, corner_radius=0, fg_color=background_color,  border_color=background_color)
        self.hide_buttons_frame = CTkFrame(self, height=270-90-8, width=170, corner_radius=10, fg_color=background_color, border_width=1, border_color=background_color)
        button_frame.pack_propagate(False)
        analyse_button = CTkButton(button_frame, text='Analyser Le Dossier', height=25,
                                       bg_color=background_color, text_color=text_color, fg_color='#7f0101',
                                       corner_radius=4, hover_color='#920101')
        start_sorting_button = CTkButton(button_frame, text='Commencer le Triage', height=25,
                                       bg_color=background_color, text_color=text_color, fg_color=button_background_color,
                                       corner_radius=4, hover_color=button_background_hover_color,
                                       command=lambda: self.button_start_on_click())
        filecheck_label = ttk.Label(button_frame, text='', font=(default_font[0], 10),
                                    foreground=text_color, background='#3D3D3D', wraplength=170)
        self.yes_button = tk.Button(button_frame, relief='flat', bd=0, activebackground='#3D3D3D', background='#3D3D3D', image=self.yes_image)
        self.no_button = tk.Button(button_frame, relief='flat', bd=0, activebackground='#3D3D3D', background='#3D3D3D', image=self.no_image)
        self.yes_to_all_button = CTkButton(button_frame, text='Oui Pour Tous', height=25,
                                       bg_color=background_color, fg_color=button_background_color,
                                       corner_radius=4, hover_color=button_background_hover_color)
        self.no_to_all_button = CTkButton(button_frame, text='Non Pour Tous', height=25,
                                       bg_color=background_color, fg_color=button_background_color,
                                       corner_radius=4, hover_color=button_background_hover_color)

        button_frame.place(x=550, y=115)
        border_frame.place(x=550, y=205)
        self.toggle_button_state('I LOVE WATERMELON!!!!!')

        analyse_button.place(relx=0.5 - analyse_button['width'] / 2 / 170, y=15)
        start_sorting_button.place(relx=0.5 - start_sorting_button['width'] / 2 / 170, y=50) #+35
        self.yes_to_all_button.place(relx=0.5 - self.yes_to_all_button['width'] / 2 / 170, y=148)
        self.no_to_all_button.place(relx=0.5 - self.no_to_all_button['width'] / 2 / 170, y=179)
        self.yes_button.place(x=13, rely=0.76)
        self.no_button.place(x=170-64-13, rely=0.76)
        filecheck_label.place(x=0, y=98)

        # trace add
        self.path_entry_var.trace_add('write', lambda *args: self.update_gui_fields(1))
        self.output_path_var.trace_add('write', lambda *args: self.update_gui_fields(2))
        self.sortingtype_entry_var.trace_add('write', lambda *args: self.update_gui_fields(3))
        self.namingtype_entry_var.trace_add('write', lambda *args: self.update_gui_fields(4))

        # debug scrolled text
        debug = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=12, width=115, font=(default_font[0], 10), fg=text_color, bg='black')

        debug.place(x=3, y=470)

a = GUI()
a.draw_gui()
a.mainloop()
