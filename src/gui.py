import os
import threading
from time import sleep
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
from customtkinter import CTkEntry, CTkButton, CTkFrame
from utils.tooltip import CustomTooltipLabel
from utils import utils
from file_operation.file_utils import FileUtils, get_folder, check_button_state, get_destination_path, get_date_taken

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Trieur D\'images')
        self.geometry('883x670+89+64')
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.configure(bg='#323232')
        self.init_variables()
        self.init_images()

    def init_variables(self):
        # checkboxes
        self.filetype_check_var = tk.StringVar(value='off')
        self.insertname_check_var = tk.StringVar(value='off')

        # entries
        self.path_entry_var = tk.StringVar(value='')
        self.output_path_var = tk.StringVar(value='')
        self.namingtype_entry_var = tk.StringVar(value='')
        self.sortingtype_entry_var = tk.StringVar(value='')
        self.filecheck_label_var = tk.StringVar(value='')

        # global button state
        self.button_state = ['1', '1', '1', '1'] # 0: invalid, red | 1: neutral, grey | 2: valid, green

        # folder
        self.folder = None

        # debug line count
        self.debug_line_count = 0

        # sorted items count
        self.moved_images = 0
        self.moved_documents = 0

        # wait var
        self.button_clicked = tk.BooleanVar(value=False)
        self.click = None

        # others
        self.load_state = False
        self.loading_job = None
        self.is_clickable_analyse = True
        self.document_blacklist = []

    def init_images(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # self.iconbitmap(base_dir + '\\assets\\app_icon.ico')
        self.yes_image = tk.PhotoImage(file=base_dir + '\\assets\\oui_64px.png')
        self.no_image = tk.PhotoImage(file=base_dir + '\\assets\\non_64px.png')
        self.tip_image = tk.PhotoImage(file=base_dir + '\\assets\\info_25px.png')

    def load_text_safe(self, text, frame_index=0):
        if self.is_clickable_analyse:
            self.stop_loading()
            return
        frames = [' ', '.', '..', '...']
        new_text = text + frames[frame_index]
        self.replace_line(new_text)
        
        frame_index = (frame_index + 1) % len(frames)
        self.loading_job = self.after(250, lambda: self.load_text_safe(text, frame_index))

    def stop_loading(self):
        if self.loading_job:
            self.after_cancel(self.loading_job)
            self.loading_job = None

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

    def button_analyse_on_click(self):
        if not self.is_clickable_analyse:
            return
        self.is_clickable_analyse = False
        path = self.path_entry_var.get()
        try:
            if self.folder:
                FileUtils.freeFolder(self.folder)
                self.folder = None

            if self.button_state[0] == '2':
                dir_basename = os.path.basename(path)
                # threading.Thread(target=lambda *args: self.load_text(f'Analyse du dossier \'{dir_basename}\' en cours')).start()
                self.stop_loading()
                self.load_text_safe(f'Analyse du dossier \'{dir_basename}\' en cours')
            self.folder = get_folder(self.button_state, path)
            sleep(1) # ahah i wasted 1 sec
            self.stop_loading()

            self.load_state = False
            if self.folder:
                self.analyse_button.configure(fg_color='#4d9b3f', hover_color='#54aa44')
                self.replace_line(f'Analyse terminée: {self.folder.contents.image_count} photos/vidéos et {self.folder.contents.other_count} autres fichiers détectés dans le dossier \'{dir_basename}\'.\n')
                self.add_line('Appuyez sur \'Commencer Le Triage\' pour commencer à les trier')
                
            else:
                self.analyse_button.configure(fg_color='#7f0101', hover_color='#920101')
            self.is_clickable_analyse = True
        except ValueError as e:
            self.stop_loading()
            self.load_state = False
            self.analyse_button.configure(fg_color='#7f0101', hover_color='#920101')
            self.replace_line(f'[ERREUR] -> {e}', '#ff3333')
            self.folder = None
            self.is_clickable_analyse = True

    def button_start_on_click(self):
        self.start_sorting_button.configure(state='disabled')
        self.analyse_button.configure(state='disabled')

        # get data
        path = self.path_entry_var.get()
        output_path = self.output_path_var.get() if self.output_path_var.get() else path
        sorting_type = self.sortingtype_entry_var.get()
        naming_type = self.namingtype_entry_var.get()
        is_sorting_documents = True if self.filetype_check_var.get() == 'on' else False
        is_inserting_date = True if self.insertname_check_var.get() == 'off' else False

        # check
        try:
            check_button_state(self.button_state, self.folder, self.insertname_check_var.get())
        except ValueError as e:
            self.add_line(f'[ERREUR] -> {e}', '#ff3333')
            self.start_sorting_button.configure(state='normal')
            self.analyse_button.configure(state='normal')
            return
        
        # move files
        if is_sorting_documents:
            self.update_blacklist()
            
        threading.Thread(target=lambda *args: self.move_files(output_path, sorting_type, naming_type, is_inserting_date, is_sorting_documents)).start()

    def button_click(self, click):
        self.click = click
        self.button_clicked.set(True)

    def update_blacklist(self):
        document_count = self.folder.contents.other_count
        self.toggle_button_state('normal')

        for i in range(document_count):
            current_path = self.folder.contents.others[i].path.decode('utf-8')
            current_name = os.path.basename(current_path)

            self.button_clicked.set(False)
            self.click = None

            self.filecheck_label_var.set(f"'{current_name}' n'est pas une image/vidéo, inclure ?")

            self.wait_variable(self.button_clicked)

            if self.click == 'yes-to-all':
                break
            elif self.click == 'yes':
                continue
            elif self.click == 'no':
                self.document_blacklist.append(i)
            else:
                for y in range(i, document_count):
                    self.document_blacklist.append(y)
                break
        
        self.toggle_button_state('THIS IS AWSOME')
        self.filecheck_label_var.set('')

    def move_files(self, output_path, sorting_type, naming_type, is_inserting_date, is_sorting_documents):
        image_count = self.folder.contents.image_count
        document_count = self.folder.contents.other_count
        for i in range(image_count):
            current_image_path = self.folder.contents.images[i].path.decode('utf-8')
            current_image_date = get_date_taken(current_image_path)
            current_destination_path = get_destination_path(current_image_path, output_path, sorting_type, naming_type, is_inserting_date, current_image_date)

            self.add_line(f'Traitement en cours: {current_image_path}')

            try:
                current_img_retval = FileUtils.moveFile(bytes(current_image_path, 'utf-8'), bytes(current_destination_path, 'utf-8'))
            except OSError as e:
                self.add_line(f'[ERREUR] Erreur lors du déplacement du fichier: {current_image_path}', '#ff3333')

            if current_img_retval == 0 and FileUtils.directoryExists(bytes(current_destination_path, 'utf-8')):
                self.moved_images += 1

        for i in range(document_count):
            if not is_sorting_documents:
                break
            if i in self.document_blacklist:
                continue
            current_document_path = self.folder.contents.others[i].path.decode('utf-8')
            current_document_date = get_date_taken(current_document_path)
            current_destination_path_doc = get_destination_path(current_document_path, output_path, sorting_type, naming_type, is_inserting_date, current_document_date)

            self.add_line(f'Traitement en cours: {current_document_path}')

            try:
                current_doc_retval = FileUtils.moveFile(bytes(current_document_path, 'utf-8'), bytes(current_destination_path_doc, 'utf-8'))
            except OSError as e:
                self.add_line(f'[ERREUR] Erreur lors du déplacement du fichier: {current_document_path}', '#ff3333')

            if current_doc_retval == 0 and FileUtils.directoryExists(bytes(current_destination_path_doc, 'utf-8')):
                self.moved_documents += 1
                
        self.add_line('      ')
        self.add_line(f'{self.moved_images} images/vidéos et {self.moved_documents} documents ont été tri avec succès', 'green')
        self.add_line('*** TRI TERMINÉ ***')
        self.add_line('      ')
        FileUtils.freeFolder(self.folder)
        self.folder = None
        self.moved_images = 0
        self.moved_documents = 0
        self.analyse_button.configure(fg_color='#7f0101', hover_color='#920101')
        self.start_sorting_button.configure(state='normal')
        self.analyse_button.configure(state='normal')

    def update_entries(self):
        # possible_state = ['2222', '2122', '2212', '2221', '2112', '2121']
        # impossible_state = [0xxx, 1xxx, 1x11, 2x11, 2x00]
        entries = [self.path_entry, self.output_path, self.sortingtype_entry, self.namingtype_entry]
        joined = ''.join(self.button_state)
        for i in range(4):
            current_entry = entries[i]
            current_state = int(joined[i])
            if current_state == 0:
                current_entry.configure(border_color=self.border_color_invalid)
            elif current_state == 1:
                current_entry.configure(border_color=self.border_color)
            else:
                current_entry.configure(border_color=self.border_color_valid)

    def update_button_state(self, field_index, value):
        '''update the global button state, field_index is the index between 1-4'''
        self.button_state[field_index-1] = value
        self.update_entries()

    def print_line_lengths(self):
        num_lines = int(self.debug.index(tk.END).split('.')[0]) - 1
        for line_num in range(1, num_lines + 1):
            line_content = self.debug.get(f"{line_num}.0", f"{line_num}.end")
            line_length = len(line_content)
            print(f"Line {line_num}: {line_length} columns")

    def remove_extra_empty_lines(self):
        self.debug.configure(state='normal')
    
        line_count = int(self.debug.index(tk.END).split('.')[0]) - 1
    
        for line_num in range(line_count, 0, -1):
            line_content = self.debug.get(f"{line_num}.0", f"{line_num}.end")
        
            if line_content.strip():
                break
            if line_num < line_count:
                self.debug.delete(f"{line_num}.0", f"{line_num+1}.0")
        self.debug.configure(state='disabled')

    def add_line(self, text, color=None):
        self.debug.configure(state='normal')
        current = int(self.debug.index(tk.END).split('.')[0]) - 1
        self.debug.insert(tk.END, text+'\n')
        line_start = f"{current}.0"
        line_end = f"{current + 1}.0"
        if color:
            self.debug.tag_add(color, line_start, line_end)
            self.debug.tag_configure(color, foreground=color)
        else:
            for tag in self.debug.tag_names(line_start):
                self.debug.tag_remove(tag, line_start, line_end)
        self.debug.yview_moveto(1.0)
        self.debug.configure(state='disabled')

    def replace_line(self, text, color=None):
        self.debug.configure(state='normal')
        previous_line_index = int(self.debug.index(tk.END).split('.')[0]) - 2
        self.debug.delete(f'{previous_line_index}.0', f'{previous_line_index}.0 lineend')
        self.debug.insert(f'{previous_line_index}.0', text+'\n')
        if previous_line_index == 0:
            line_start = f"{previous_line_index + 1}.0"
            line_end = f"{previous_line_index + 2}.0"
        else:
            line_start = f"{previous_line_index}.0"
            line_end = f"{previous_line_index + 1}.0"
        if color:   
            self.debug.tag_add(color, line_start, line_end)
            self.debug.tag_configure(color, foreground=color)
        else:
            for tag in self.debug.tag_names(line_start):
                self.debug.tag_remove(tag, line_start, line_end)

        self.debug.configure(state='disabled')
        self.remove_extra_empty_lines()
        
    def update_gui_fields(self, field_index, *args):
        if field_index == 1:
            # update analyse button bg color
            self.analyse_button.configure(fg_color='#7f0101', hover_color='#920101')

            # is path entry
            if len(self.path_entry_var.get()) == 0:
                # is neutral
                self.update_button_state(field_index, '1')
                return
            if FileUtils.directoryExists(bytes(self.path_entry_var.get(), 'utf-8')):
                # is valid
                self.update_button_state(field_index, '2')
            else:
                # is invalid
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
            if utils.is_field_type_valid(self.sortingtype_entry_var.get()):
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
            if utils.is_field_type_valid(self.namingtype_entry_var.get(), 1):
                # is valid
                self.update_button_state(field_index, '2')
            else:
                # is invalid
                self.update_button_state(field_index, '0')

    def on_close(self):
        if self.folder:
            FileUtils.freeFolder(self.folder)
        self.destroy()
        os._exit(0)

    def draw_gui(self):
        # texts
        self.title_text = 'Trieur D\'images - Developpé Par Bladeeee™ ;)'
        explaination_text = 'Ce programme permet de trier et nommer par date des photos et des documents en masse.'
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
            "    │       ├── IMG_0001.jpg\n"
            "    │       └── IMG_0002.jpg\n"
            "    └── 2023/\n"
            "        └── 2023-12/\n"
            "            ├── IMG_0003.jpg\n"
            "            └── IMG_0004.jpg\n"
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
        ttk_styling.map('BlackCheckbutton.TCheckbutton',
          background=[('active', background_color)],
          foreground=[('active', text_color)])
        

        # explaination text
        explaination_frame = ttk.Frame(self, style='BlackFrame.TFrame')

        title_label = ttk.Label(self, text=self.title_text, foreground=text_color, background=background_color, font=default_font)
        explaination_label = ttk.Label(explaination_frame, text=explaination_text, foreground=text_color, background=background_color, font=caption_font)

        # explaination text layout
        title_label.pack(pady=15)
        explaination_label.pack(pady=8)
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
        sortingtype_button_tip = tk.Button(sortingtype_frame, relief='flat', highlightthickness=0, bd=0, activebackground=background_color, background=background_color, image=self.tip_image)

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
        namingtype_button_tip = tk.Button(namingtype_frame, relief='flat', bd=0, highlightthickness=0, activebackground=background_color, background=background_color, image=self.tip_image)

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
        additional_tip_label.place(x=5, y=346)

        # buttons
        button_frame = CTkFrame(self, height=270, width=170, corner_radius=10, fg_color='#3D3D3D', border_width=1, border_color='#3D3D3D')
        border_frame = CTkFrame(self, height=8, width=170, corner_radius=0, fg_color=background_color,  border_color=background_color)
        self.hide_buttons_frame = CTkFrame(self, height=270-90-8, width=170, corner_radius=10, fg_color=background_color, border_width=1, border_color=background_color)
        button_frame.pack_propagate(False)
        self.analyse_button = CTkButton(button_frame, text='Analyser Le Dossier', height=25,
                                       bg_color='#3D3D3D', text_color=text_color, fg_color='#7f0101',
                                       corner_radius=4, hover_color='#920101',
                                       command=lambda *args: threading.Thread(target=lambda *args: self.button_analyse_on_click()).start())
        self.start_sorting_button = CTkButton(button_frame, text='Commencer le Triage', height=25,
                                       bg_color='#3D3D3D', text_color=text_color, fg_color=button_background_color,
                                       corner_radius=4, hover_color=button_background_hover_color,
                                       command=lambda: self.button_start_on_click())
        filecheck_label = ttk.Label(button_frame, text='', font=(default_font[0], 9),
                                    foreground=text_color, textvariable=self.filecheck_label_var,
                                    background='#3D3D3D', wraplength=170)
        self.yes_button = tk.Button(button_frame, relief='flat', bd=0, highlightthickness=0, activebackground='#3D3D3D',
                                    background='#3D3D3D', image=self.yes_image, command=lambda: self.button_click('yes'))
        self.no_button = tk.Button(button_frame, relief='flat', bd=0, highlightthickness=0,
                                   activebackground='#3D3D3D', command=lambda: self.button_click('no'), background='#3D3D3D', image=self.no_image)
        self.yes_to_all_button = CTkButton(button_frame, text='Oui Pour Tous', height=25,
                                       bg_color='#3D3D3D', fg_color=button_background_color,
                                       command=lambda: self.button_click('yes-to-all'),
                                       corner_radius=4, hover_color=button_background_hover_color)
        self.no_to_all_button = CTkButton(button_frame, text='Non Pour Tous', height=25,
                                       bg_color='#3D3D3D', fg_color=button_background_color, command=lambda: self.button_click('no-to-all'),
                                       corner_radius=4, hover_color=button_background_hover_color)

        button_frame.place(x=550, y=115)
        border_frame.place(x=550, y=205)
        self.toggle_button_state('I LOVE WATERMELON!!!!!')

        self.analyse_button.place(relx=0.5 - self.analyse_button['width'] / 2 / 170, y=15)
        self.start_sorting_button.place(relx=0.5 - self.start_sorting_button['width'] / 2 / 170, y=50) #+35
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

        # hover tips
        # path_entry_tip_text
        # output_path_tip_text
        CustomTooltipLabel(anchor_widget=path_entry_label, text=path_entry_tip_text,
                           background='#2c2c2c', font=tip_font,
                           wraplength=utils.get_wraplength(self, path_entry_label),
                           foreground=text_color, hover_delay=500, border=1)
        
        CustomTooltipLabel(anchor_widget=output_path_label, text=output_path_tip_text,
                           background='#2c2c2c', font=tip_font,
                           wraplength=utils.get_wraplength(self, path_entry_label),
                           foreground=text_color, hover_delay=500, border=1)


        # debug scrolled text
        self.debug = scrolledtext.ScrolledText(self, wrap=tk.WORD, state='disabled', height=12,
                                               width=122, font=(default_font[0], 10),
                                               fg=text_color, bg='black')
        self.debug.tag_configure("sel", background='black', foreground=text_color)

        self.debug.place(x=3, y=470)
