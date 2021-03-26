from io import BytesIO
from tkinter import ttk, filedialog, simpledialog
import os
from tkinter import *
import pickle
import requests
from to_csv import create_report
from PIL import ImageTk
from text_classification import *

from messages_logic import create_single_conversation_wordcloud, create_single_participant_wordcloud, \
    create_messenger_statistics, \
    create_graph


def shorten_file_path(path, max_length):
    if len(path) > max_length:
        splitted = path.split(r"/")
        if len(splitted) > 2:
            return "{}/.../{}/{}/".format(splitted[0], splitted[-2], splitted[-1])
    return path


def first_start():
    with open("config.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        if "first_start" in line:
            if line.split("=")[1] == "1":
                with open("config.txt", "w") as f:
                    f.write("first_start=0")
                return True

    return False


class App:
    def __init__(self, master):
        self.master = master

        # Main window configuration
        self.master.iconbitmap('app_icon.ico')
        self.master.title("Messenger to Word Cloud")
        self.master.geometry('850x520+600+200')

        window.minsize(850, 520)
        self.master.resizable(True, False)
        self.master.configure(bg="white")

        self.history = []
        self.templates = []
        if first_start():
            self.initiate_pickle("history")
            self.initiate_pickle("templates")

        # Default values
        self.image_path = "%s/Masks/man.png" % os.curdir
        self.font = "DroidSansMono.ttf"

        self.MIN_LENGTH = 4
        self.single_person_full_path = ""
        self.single_conv_full_path = ""
        self.color = "Random"

        self.var_single_conv_path = StringVar()
        self.var_single_person_path = StringVar()

        self.file_label = StringVar()
        self.varImage = StringVar()
        self.varFont = StringVar()
        self.varName = StringVar()
        self.varCombined = IntVar()
        self.varSeparated = IntVar()
        self.varLength = IntVar()
        self.cloudColorCombo = StringVar()

        self.mask_image = None
        self.canvas_cloud_color = None

        # Status bar configuration
        self.statusbar = Label(master, text="Welcome to Worcloud Messenger App!", bd=1, relief=SUNKEN, anchor=W,
                               width=1000, font=("Century Gothic", 8), fg="red")
        self.statusbar.after(5000, self.clear_status_bar)
        self.statusbar.pack(side=BOTTOM, ipady=5)

        # Menu configuration
        menubar = Menu(self.master)
        self.master["menu"] = menubar
        file_menu = Menu(menubar)
        file_menu.add_command(label="Choose single conversation directory", underline=0,
                              command=lambda: self.choose_file("conv"))
        file_menu.add_command(label="Choose inbox directory", underline=0, command=lambda: self.choose_file("person"))
        history_menu = Menu(menubar)

        history_menu.add_command(label="Show history", underline=0, command=lambda: self.show_listbox("history"))

        template_menu = Menu(menubar)
        template_menu.add_command(label="Save current state", underline=0,
                                  command=lambda: self.save_current_state("templates"))
        template_menu.add_command(label="Show templates", underline=0, command=lambda: self.show_listbox("templates"))

        menubar.add_cascade(label="Paths", menu=file_menu, underline=0)
        menubar.add_cascade(label="History", menu=history_menu, underline=0)
        menubar.add_cascade(label="Templates", menu=template_menu, underline=0)
        menubar.add_command(label="Help", command=lambda: os.startfile('Help.txt'))

        # Tabs configuration
        self.tab_control = ttk.Notebook(self.master)
        self.tab_frame_wordcloud = Frame(self.tab_control, bg="white")
        self.tab_frame_stats = Frame(self.tab_control, bg="white")
        self.tab_control.add(self.tab_frame_wordcloud, text='Wordcloud')
        self.tab_control.add(self.tab_frame_stats, text='Your stats')
        self.tab_control.pack(expand=1, fill="both")

        # Loading history and templates
        self.load_from_pickle("history")
        self.load_from_pickle("templates")

        self.create_main_window()

    # Main window functions
    def choose_file(self, file_type):
        # my_filetypes = [('all files', '.*''.*'), ('text files', 'txt')]
        if file_type == "conv":
            dialog_title = "Select directory with conversation files"
        elif file_type == "person":
            dialog_title = "Select inbox directory"
        else:
            return
        directory = filedialog.askdirectory(parent=window,
                                            initialdir=os.getcwd(),
                                            title=dialog_title)
        if directory == "":
            return
        if file_type == "conv":
            self.single_conv_full_path = directory
            self.var_single_conv_path.set(f"{os.path.basename(directory).split('_')[0]}/")
            self.update_status("Single conversation path set to {}".format(shorten_file_path(directory, 50)))
        elif file_type == "person":
            self.single_person_full_path = directory
            self.var_single_person_path.set(f"{os.path.basename(directory).split('_')[0]}/")
            self.update_status("Inbox path set to {}".format(directory))

    def initiate_pickle(self, what):  # only once
        if what == "history":
            with open("history", "wb") as f:
                pickle.dump(self.history, f)
        elif what == "templates":
            with open("templates", "wb") as f:
                pickle.dump(self.templates, f)

    def save_current_state(self, what):
        if what == "history":
            self.history.append({"mask": self.mask_image.cget("image"),
                                 "mask_path": self.image_path,
                                 "cloud_color": self.cloudColorCombo.get(),
                                 "font": self.font,
                                 "min_length": self.varLength.get(),
                                 "separate": self.varSeparated.get(),
                                 "combined": self.varCombined.get(),
                                 "conv_path": self.single_conv_full_path,
                                 "person_path": self.single_person_full_path,
                                 "person": self.varName.get()})
            try:
                with open("history", "wb") as f:
                    pickle.dump(self.history, f)
            except Exception as e:
                print(e)
            self.update_status("State saved in file 'history.pkl'!")

        elif what == "templates":
            name = simpledialog.askstring(title="Template",
                                          prompt="Enter template name")
            if name != "":
                self.templates.append({"temp_name": name,
                                       "mask": self.mask_image.cget("image"),
                                       "mask_path": self.image_path,
                                       "cloud_color": self.cloudColorCombo.get(),
                                       "font": self.font,
                                       "min_length": self.varLength.get(),
                                       "separate": self.varSeparated.get(),
                                       "combined": self.varCombined.get(),
                                       "conv_path": self.single_conv_full_path,
                                       "person_path": self.single_person_full_path,
                                       "person": self.varName.get()})
            try:
                with open("templates", "wb") as f:
                    pickle.dump(self.templates, f)
            except Exception as e:
                print(e)
            self.update_status("State saved in file 'templates.pkl'!")

    def print_state(self, num, what):
        temp_str = ""
        if what == "history":
            state = self.history[num]
            temp_str = "Mask: {}, Color: {}, Font: {}, Min. length: {}{}{}, Conv: {}, Person: {}, Name: {}".format(
                os.path.basename(state["mask_path"]) if isinstance(state["mask_path"], str) else state["mask_path"],
                state["cloud_color"], state["font"], state["min_length"],
                ", separate" if state["separate"] else "", ", combinded" if state["combined"] else "",
                os.path.basename(state["conv_path"]).split("_")[0] if os.path.basename(state["conv_path"]).split("_")[
                                                                          0] != "" else "None",
                os.path.basename(state["person_path"]) if os.path.basename(state["person_path"]) != "" else "None",
                state["person"] if state["person"] != "" else "None")
        elif what == "templates":
            state = self.templates[num]
            temp_str = str(state["temp_name"])

        return temp_str

    def show_listbox(self, what):
        self.load_from_pickle(what)
        choice = 0
        listbox_window = Tk()
        scrollbar_y = Scrollbar(listbox_window)
        scrollbar_y.pack(side=RIGHT, fill=Y)

        listbox_window.title("Choose saved state")
        listbox_window.geometry('1200x300') if what == "history" else listbox_window.geometry('500x300')

        displayed_list = Listbox(listbox_window, width=110 if what == "history" else 30, yscrollcommand=scrollbar_y.set,
                                 font=('Century Gothic', 10))
        for num in range(len(self.history if what == "history" else self.templates)):
            displayed_list.insert(END, self.print_state(num, what))

        displayed_list.pack(side=LEFT, fill=BOTH)
        scrollbar_y.config(command=displayed_list.yview)

        def clear_list():
            for num in range(displayed_list.size()):
                self.delete_from_pickle(0, what)
            displayed_list.delete(0, 'end')
            self.load_from_pickle(what)
            self.update_status("Cleared all rows!!")

        def delete_choice():
            if len(displayed_list.curselection()) != 0:
                choice = displayed_list.curselection()[0]
                self.delete_from_pickle(choice, what)
                self.load_from_pickle(what)
                displayed_list.delete(0, 'end')
                for num in range(len(self.history if what == "history" else self.templates)):
                    displayed_list.insert(END, self.print_state(num, what))

                self.update_status("Position number {} deleted from history!".format(choice + 1))
            else:
                self.update_status("History is empty!!")

        def save_choice():
            nonlocal choice

            if len(displayed_list.curselection()) != 0:
                choice = displayed_list.curselection()[0]
                state = self.history[choice] if what == "history" else self.templates[choice]
                # LOAD EVERYTHING
                img = ImageTk.PhotoImage(
                    ImageTk.Image.open(state["mask_path"]).resize((200, 200), ImageTk.Image.ANTIALIAS))
                self.mask_image.configure(image=img)
                self.mask_image.image = img
                self.image_path = state["mask_path"]
                self.varImage.set("MASK: %s" % (
                    os.path.basename(self.image_path) if isinstance(self.image_path, str) else "From url"))
                self.cloudColorCombo.set(state["cloud_color"])
                if state["cloud_color"] not in ["Random", "From mask"]:
                    self.canvas_cloud_color.configure(bg=state["cloud_color"])
                # self.COLOR=state["cloud_color"]
                self.font = state["font"]
                self.varFont.set("FONT: %s" % (os.path.basename(state["font"])))
                self.varLength.set(state["min_length"])
                self.varSeparated.set(state["separate"])
                self.varCombined.set(state["combined"])
                self.single_conv_full_path = state["conv_path"]
                self.var_single_conv_path.set("{}/".format(os.path.basename(state["conv_path"]).split('_')[0]))
                self.single_person_full_path = state["person_path"]
                self.var_single_person_path.set("{}/".format(os.path.basename(state["person_path"]).split('_')[0]))
                self.varName.set(state["person"])
                self.update_status("Loaded chosen state!")
            else:
                self.update_status("History is empty!!")
            listbox_window.destroy()

        close_delete = Button(listbox_window, text="Delete", command=delete_choice)
        close_delete.pack(side=RIGHT, padx=10)

        close_save = Button(listbox_window, text="Load", command=save_choice)
        close_save.pack(side=RIGHT)

        close_clear = Button(listbox_window, text="Clear", command=clear_list)
        close_clear.pack(side=RIGHT, padx=10)

        listbox_window.mainloop()

    def delete_from_pickle(self, num, what):
        if what == "history":
            del self.history[num]
        elif what == "templates":
            del self.templates[num]

        try:
            with open("history" if what == "history" else "templates", "wb") as f:
                pickle.dump(self.history if what == "history" else self.templates, f)
        except Exception as e:
            print(e)

    def load_from_pickle(self, what):
        try:
            with open("history" if what == "history" else "templates", "rb") as f:
                if what == "history":
                    self.history = pickle.load(f)
                elif what == "templates":
                    self.templates = pickle.load(f)
        except Exception as e:
            print(e)
        self.update_status(f"Loaded {what}!")

    def clear_status_bar(self):
        self.statusbar.config(text="")

    def update_status(self, message):
        self.statusbar.config(text=message)
        self.statusbar.after(5000, self.clear_status_bar)

    def create_main_window(self):

        def combo_changed(index, value, op):
            if self.canvas_cloud_color is not None:
                if self.cloudColorCombo.get() not in ["Random", "From mask"]:
                    self.canvas_cloud_color.configure(bg=self.cloudColorCombo.get())
                else:
                    self.canvas_cloud_color.configure(bg="white")

        # Change canvas color on color combo change
        self.cloudColorCombo.trace('w', combo_changed)

        # First tab functions
        def clicked_name():
            self.varName.set(entry_participant.get())
            label_participant_result.configure(text=entry_participant.get())
            entry_participant.delete(0, END)
            entry_participant.insert(0, "")
            self.update_status("Participant set to '{}'!".format(self.varName.get()))

        def generate_one_conv_wordcloud():
            self.save_current_state("history")
            self.MIN_LENGTH = int(spinbox_min_word_length.get())
            self.color = combobox_colors.get()
            result = create_single_conversation_wordcloud(self.varSeparated.get(), self.varCombined.get(),
                                                          self.single_conv_full_path, self.image_path,
                                                          self.varLength.get(), self.font,
                                                          self.color)
            if result is None:
                self.update_status("Wrong directory!")
            else:
                self.update_status("Generated wordcloud!")

        def generate_single_person_wordcloud():
            self.save_current_state("history")
            self.MIN_LENGTH = int(spinbox_min_word_length.get())
            self.color = combobox_colors.get()
            result = create_single_participant_wordcloud(self.single_person_full_path, self.varName.get(),
                                                         self.image_path,
                                                         self.varLength.get(),
                                                         self.font, self.color)
            if result is None:
                self.update_status("Wrong directory!")
            else:
                self.update_status("Generated wordcloud!")

        def clicked_font_update():
            filename = filedialog.askopenfilename(initialdir="%s/Fonts" % (os.curdir),
                                                  title="Select file", filetypes=[
                    ("Font files", ".ttf")])  # show an "Open" dialog box and return the path to the selected file
            if filename == "":
                return
            self.font = filename
            self.varFont.set("FONT: %s" % (os.path.basename(filename)))
            label_font.configure(text="FONT: %s" % (os.path.basename(filename)))
            self.update_status("Wordcloud font set to '{}'!".format(os.path.basename(filename)))

        def update_mask_canva(img):
            self.mask_image.configure(image=img)
            self.mask_image.image = img

        def clicked_mask_update():
            filename = filedialog.askopenfilename(initialdir="%s/Masks" % (os.curdir),
                                                  title="Select mask file", filetypes=[
                    ("Image files", ".jpg .png")])  # show an "Open" dialog box and return the path to the selected file
            if filename == "":
                return
            self.image_path = filename
            self.varImage.set("MASK: %s" % (os.path.basename(filename)))
            img = ImageTk.PhotoImage(ImageTk.Image.open(self.image_path).resize((200, 200), ImageTk.Image.ANTIALIAS))
            update_mask_canva(img)
            self.update_status("Wordcloud mask set to '{}'!".format(self.image_path))

        def clicked_mask_update_url():
            user_inp = simpledialog.askstring(title="Test",
                                              prompt="Enter image url address")
            if user_inp is None:
                return

            try:
                response = requests.get(user_inp)
                self.image_path = BytesIO(response.content)
                img = ImageTk.PhotoImage(
                    ImageTk.Image.open(BytesIO(response.content)).resize((200, 200), ImageTk.Image.ANTIALIAS))
            except Exception as e:
                print(e)
                self.update_status("Wrong file format! Can't load!")
                return

            update_mask_canva(img)
            self.update_status("Wordcloud mask set to image from '{}'!".format(user_inp))

        # ----------------------------------------------  WORDCLOUD TAB  ----------------------------------------------
        # ----------------------------------------------  FIRST COLUMN  -----------------------------------------------
        frame_wordcloud_configuration = LabelFrame(self.tab_frame_wordcloud, text="Customize your wordcloud",
                                                   bg="white")
        frame_wordcloud_configuration.columnconfigure(0, pad=30)
        frame_wordcloud_configuration.pack(side=LEFT, fill=Y, expand=True)

        # --------------------------------------------------  MASK  ---------------------------------------------------
        lbl_mask_path = Label(frame_wordcloud_configuration, textvariable=self.varImage, bg="white")
        lbl_mask_path.grid(row=0, column=0, columnspan=1, sticky="W", padx=10)
        lbl_mask_path.config(font=("Arial", 14))
        self.varImage.set("MASK: %s" % (os.path.basename(self.image_path)))

        button_change_mask_pc = Button(frame_wordcloud_configuration, text="FROM PC", command=clicked_mask_update,
                                       bg="#0A353A",
                                       fg="white")
        button_change_mask_pc.grid(row=1, column=0, sticky="W", rowspan=2, padx=10)
        button_change_mask_pc.config(font=("Arial", 14), width=9)

        button_change_mask_url = Button(frame_wordcloud_configuration, text="FROM URL", command=clicked_mask_update_url,
                                        bg="#0A353A",
                                        fg="white")
        button_change_mask_url.grid(row=1, column=0, sticky="E", rowspan=2, padx=10)
        button_change_mask_url.config(font=("Arial", 14), width=9)

        img = ImageTk.PhotoImage(ImageTk.Image.open(self.image_path).resize((200, 200), ImageTk.Image.ANTIALIAS))
        self.mask_image = Label(frame_wordcloud_configuration, image=img, bg="white")
        self.mask_image.grid(row=0, column=1, columnspan=2, rowspan=3, sticky="E")

        # -------------------------------------------------  COLORS  --------------------------------------------------
        label_cloud_color = Label(frame_wordcloud_configuration, text="CLOUD COLOR: ", bg="white")
        label_cloud_color.grid(row=3, column=0, sticky="W", padx=10, pady=20)
        label_cloud_color.config(font=("Arial", 14))

        combobox_colors = ttk.Combobox(frame_wordcloud_configuration, textvar=self.cloudColorCombo,
                                       values=["Random", "From mask", "Blue", "Cyan", "Green", "Magenta", "Orange",
                                               "Red", "Yellow"])

        combobox_colors.current(3)
        combobox_colors.grid(row=3, column=1)
        combobox_colors.config(font=("Arial", 12), width=10)

        self.canvas_cloud_color = Canvas(frame_wordcloud_configuration, height=20, width=20,
                                         bg=self.cloudColorCombo.get())
        self.canvas_cloud_color.grid(row=3, column=0, sticky="E", padx=130)

        # --------------------------------------------------  FONT  ---------------------------------------------------
        label_font = Label(frame_wordcloud_configuration, textvariable=self.varFont, bg="white")
        label_font.grid(row=5, column=0, sticky="W", pady=20, padx=10)
        label_font.config(font=("Arial", 14))
        self.varFont.set("FONT: %s" % self.font)

        button_change_font = Button(frame_wordcloud_configuration, text="CHANGE FONT", command=clicked_font_update,
                                    bg="#0A353A",
                                    fg="white")
        button_change_font.grid(row=5, column=1)
        button_change_font.config(font=("Arial", 10), width=14)

        # -----------------------------------------------  MIN LENGTH  ------------------------------------------------

        label_min_word_length = Label(frame_wordcloud_configuration, text="MINIMUM WORD LENGTH: ", bg="white")
        label_min_word_length.grid(row=6, column=0, sticky="W", pady=10, padx=10)
        label_min_word_length.config(font=("Arial", 14))

        spinbox_min_word_length = Spinbox(frame_wordcloud_configuration, from_=1, to=10, width=4,
                                          textvariable=self.varLength)
        spinbox_min_word_length.grid(row=6, column=1)
        spinbox_min_word_length.config(font=("Arial", 14), width=10)
        self.varLength.set(4)

        # ----------------------------------------------  SECOND COLUMN  -----------------------------------------------
        right_frame = Frame(self.tab_frame_wordcloud, width=600, height=200, bg="white")

        right_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # ----------------------------------------------  CONVERSATIONS  -----------------------------------------------
        labelframe_single_conv = LabelFrame(right_frame, text="Single conversation", bg="white")
        labelframe_single_conv.pack(side=TOP, fill=X, expand=True, anchor=N)
        labelframe_single_conv.grid_columnconfigure(0, weight=1)
        labelframe_single_conv.grid_columnconfigure(1, weight=1)
        check_separate = Checkbutton(labelframe_single_conv, text="SEPARATE", variable=self.varSeparated, bg="white")
        check_separate.grid(column=0, row=1, sticky="W", padx=5)
        check_separate.config(font=("Arial", 12))

        check_combined = Checkbutton(labelframe_single_conv, text="COMBINED", variable=self.varCombined, bg="white")
        check_combined.grid(column=0, row=2, sticky="W", padx=5)
        check_combined.config(font=("Arial", 12))

        label_single_conv_path = Label(labelframe_single_conv, text="CONVERSATION'S PATH:", bg="white")
        label_single_conv_path.grid(column=0, row=4, sticky="W", padx=5)
        label_single_conv_path.config(font=("Arial", 12))

        label_single_conv_path_result = Label(labelframe_single_conv, textvariable=self.var_single_conv_path,
                                              bg="white")
        label_single_conv_path_result.grid(column=0, row=5, sticky="W", padx=5)
        label_single_conv_path_result.config(font=("Arial", 12))

        button_single_conv = Button(labelframe_single_conv, text=". . .", command=lambda: self.choose_file("conv"))
        button_single_conv.grid(column=1, row=4, sticky="E", padx=5)

        button_generate_one_conv = Button(labelframe_single_conv, text="GENERATE", command=generate_one_conv_wordcloud,
                                          bg="#0A353A", fg="white")
        button_generate_one_conv.grid(column=0, row=6, sticky="WE", columnspan=2)

        # ----------------------------------------------  SINGLE PERSON  -----------------------------------------------
        labelframe_person = LabelFrame(right_frame, text="Single person", bg="white")
        labelframe_person.pack(side=BOTTOM, fill=X, expand=True, anchor=S)
        labelframe_person.grid_columnconfigure(0, weight=1)
        labelframe_person.grid_columnconfigure(1, weight=1)

        label_participant = Label(labelframe_person, text="PARTICIPANT'S NAME:", font=("Arial", 12), bg="white")
        label_participant.grid(column=0, row=1, sticky="W")

        label_participant_result = Label(labelframe_person, textvariable=self.varName, font=("Arial", 12), bg="white")

        label_participant_result.grid(column=0, row=2, sticky="W")

        entry_participant = Entry(labelframe_person, width=20, font=("Arial", 12))

        entry_participant.grid(column=0, row=4, sticky="W")

        button_entry_participant = Button(labelframe_person, text="Enter", command=clicked_name)

        button_entry_participant.grid(column=1, row=4, sticky="E")

        label_single_person_path = Label(labelframe_person, text="Inbox path:", font=("Arial", 12), bg="white")

        label_single_person_path.grid(column=0, row=5, sticky="W")

        label_single_person_path_result = Label(labelframe_person, textvariable=self.var_single_person_path, bg="white")

        label_single_person_path_result.grid(column=0, row=6, sticky="W")

        button_single_person_path = Button(labelframe_person, text=". . .", command=lambda: self.choose_file("person"))
        button_single_person_path.grid(column=1, row=5, sticky="E")

        btn_single = Button(labelframe_person, text="GENERATE", command=generate_single_person_wordcloud, bg="#0A353A",
                            fg="white")

        btn_single.grid(column=0, row=7, sticky="WE", columnspan=2)

        # ------------------------------------------------  STATS TAB  -------------------------------------------------

        # Stats tab functions
        def prepare_all_convs_frames(path):
            for child in scroll_frame.scrolled_frame.winfo_children():
                child.destroy()
            self.frames_with_convs.clear()
            filename_load = simpledialog.askstring(title="Wanna load?",
                                                   prompt="If You want to load results from a file, enter filename and click 'OK'"
                                                          "\nElse click 'Cancel'")

            filename_save = simpledialog.askstring(title="Wanna save?",
                                                   prompt="If You want to save results to a file, enter filename and click 'OK'"
                                                          "\nElse click 'Cancel'")
            if filename_load is not None:
                try:
                    with open(f"{os.curdir}/Files/{filename_load}", "rb") as f:
                        all_stats = pickle.load(f)
                except Exception as e:
                    print("Caught {", e, "}")
                    all_stats = create_messenger_statistics(path)
            else:
                all_stats = create_messenger_statistics(path)

            if all_stats == {} or all_stats is None:
                self.update_status("Wrong directory!")
                return
            counter = 0
            total_messages = sum(sum(conv["msg_count"].values()) for conv in all_stats.values())
            for conv, value in all_stats.items():
                if len(value["msg_count"]) > 1:
                    counter += 1
                    self.frames_with_convs.append(FrameWithConv(scroll_frame.scrolled_frame,
                                                                conv.split("_")[0],
                                                                counter,
                                                                value,
                                                                total_messages))
            if filename_save is not None:
                try:
                    with open(f"{os.curdir}/Files/{filename_save}", "wb") as f:
                        pickle.dump(all_stats, f)
                except Exception as e:
                    print(e)

        def save_all_convs(type):
            result_list = []
            if len(self.frames_with_convs) == 0:
                self.update_status("No conversations to save!")
                return
            total_messages = self.frames_with_convs[0].total
            for frame in self.frames_with_convs:
                name = frame.full_name
                suma = sum(frame.details["msg_count"].values())
                percent = "{:05.2f}%".format((suma / total_messages) * 100)
                result_list.append([name, suma, percent])

            if type == "csv":
                filename = simpledialog.askstring(title="Save to CSV",
                                                  prompt="Enter CSV filename (without .csv)")
                if filename is None:
                    return
                create_report(result_list, filename)
            elif type == "txt":
                filename = simpledialog.askstring(title="Save to TXT",
                                                  prompt="Enter TXT filename (without .txt)")
                if filename is None:
                    return
                with open(f"{os.curdir}/Files/{filename}.txt", "w+") as f:
                    f.write("{:50}\t|{:10}\t|{:5}\n".format("Conversation name", "Messages", "% of all messages"))
                    f.write("-" * 72)
                    for row in result_list:
                        f.write("\n{:50}\t|{:10}\t|{:5}".format(row[0], str(row[1]), row[2]))

        varName = StringVar()

        def search_conversations():
            searched_name = varName.get()
            varName.set("")
            for frame in self.frames_with_convs:
                frame.frame.pack_forget()
            for frame in filter(lambda a: searched_name in a.full_name, self.frames_with_convs):
                frame.frame.pack(side=TOP, expand=True, fill=BOTH, pady=5, padx=15, ipady=10)

        # Top section

        frame_top_section = Frame(self.tab_frame_stats, bg="white", highlightbackground="black", highlightthickness=2)
        frame_top_section.pack(side=TOP, fill=BOTH, expand=True)

        button_inbox = Button(frame_top_section, text="Choose inbox", bg="#0A353A", fg="white",
                              font=("Arial", 14),
                              command=lambda: self.choose_file("person"))
        button_inbox.pack(side=LEFT, pady=10, padx=10)

        button_analyze = Button(frame_top_section, text="Analyze", bg="#0A353A", fg="white",
                                font=("Arial", 14),
                                command=lambda: prepare_all_convs_frames(self.single_person_full_path))
        button_analyze.pack(side=LEFT, fill="x", expand=True, pady=10, padx=10)

        entry_participant_search = Entry(frame_top_section, bg="white", font=("Arial", 14), textvariable=varName)
        entry_participant_search.pack(side=LEFT, expand=True)

        button_participant_search = Button(frame_top_section, text="Search", bg="#0A353A", fg="white",
                                           font=("Arial", 14),
                                           command=search_conversations)
        button_participant_search.pack(side=LEFT, expand=True)

        button_save_all = Button(frame_top_section, text="Save ranking", bg="#0A353A", fg="white",
                                 font=("Arial", 14),
                                 command=lambda: save_all_convs("txt"))
        button_save_all.pack(side=LEFT, pady=10, padx=10)

        # Second section - table header

        frame_header = Frame(self.tab_frame_stats, bg=self.tab_frame_stats.cget('bg'))
        frame_header.pack(side=TOP, fill=BOTH, expand=True, padx=90)

        header_conv = Label(frame_header, bg=self.tab_frame_stats.cget('bg'), text="Conversation", font=("Arial", 14))
        header_conv.pack(side=LEFT)

        header_messages = Label(frame_header, bg=self.tab_frame_stats.cget('bg'), text="% of all         Messages  ",
                                font=("Arial", 14))
        header_messages.pack(side=RIGHT, anchor=W, padx=95)

        # Bottom section - all analysed conversations

        frame_all = Frame(self.tab_frame_stats, bg=self.tab_frame_stats.cget('bg'))
        frame_all.pack(side=BOTTOM, fill=BOTH, expand=True)

        scroll_frame = ScrollableFrame(frame_all, bg=frame_all.cget('bg'))
        scroll_frame.pack(side=TOP, fill=BOTH, expand=True)
        scroll_frame.configure()
        self.frames_with_convs = []

        window.mainloop()


class FrameWithConv:
    def __init__(self, master, name, id, details, total):
        """
        Creates a frame containing data about single conversation

        :param master: master frame
        :param name: conversation's name
        :param id: conversation's "place" (sorted by total messages descending)
        :param details: dictionary containing data about specific conversation
        :param total: total number of messages inside inbox
        """
        self.master = master
        self.total = total
        self.details = details
        self.frame = Frame(self.master, highlightbackground="white", highlightthickness=2, bg="#305854")
        if id == 1:
            self.frame.configure(bg="#B8860B")  # Golden
        if id == 2:
            self.frame.configure(bg="#C0C0C0")  # Silver
        if id == 3:
            self.frame.configure(bg="#964B00")  # Bronze
        self.frame.pack(side=TOP, expand=True, fill=BOTH, pady=5, padx=15, ipady=10)

        self.full_name = name
        self.name = name if len(name) < 22 else name[:19] + "..."  # Short version of conversation's name

        Label(self.frame, text="{}.".format(id), bg=self.frame.cget('bg'), fg="white", font=("Century Gothic", 14),
              width=5).pack(
            side=LEFT)
        Label(self.frame, text="{}".format(self.name), bg=self.frame.cget('bg'), fg="white",
              font=("Century Gothic", 14)).pack(side=LEFT)
        Button(self.frame, text="SHOW MORE", bg="white", font=("Century Gothic", 12),
               command=lambda: self.show_more(details)).pack(
            side=RIGHT, padx=10)
        Label(self.frame, text="{}".format(sum(details["msg_count"].values())), bg=self.frame.cget('bg'), fg="white",
              font=("Century Gothic", 14), width=7).pack(
            side=RIGHT, padx=20)
        Label(self.frame, text="{:05.2f}%".format((sum(details["msg_count"].values()) / total) * 100),
              bg=self.frame.cget('bg'), fg="white", font=("Century Gothic", 14)).pack(
            side=RIGHT, padx=20)

    def show_more(self, details):
        self.showMore = DetailsWindow(self.master, details, self.name)


class DetailsWindow(Toplevel):

    def __init__(self, master, details, name, **kw):
        """
        Creates Toplevel window containing detailed conversation's statistics

        :param master: master frame
        :param details: dictionary containing data about specific conversation
        :param name: conversation's name
        """
        super().__init__(master=master, **kw)
        self.master = master
        self.configure(bg="white")
        self.frame_up = Frame(self, bg=self.cget('bg'))
        self.frame_up.pack(side=TOP, fill=BOTH, expand=True)

        self.frame_down = Frame(self, bg=self.cget('bg'))
        self.frame_down.pack(side=BOTTOM, fill=BOTH, expand=True, pady=20)

        self.frame_buttons = Frame(self.frame_down, bg=self.frame_down.cget('bg'))
        self.frame_buttons.pack(side=TOP, fill=BOTH, expand=True)

        scroll = ScrollableFrame(self, bg=self.cget('bg'))
        scroll.pack(side=BOTTOM, fill=BOTH, expand=True)

        tl = scroll.scrolled_frame
        tl.configure(bg="white")
        self.geometry("900x300+600+300")  # Change
        self.title("{}'s details".format(name))

        def save_details(detailed_info, format):
            """
            Saves details from a conversation to file with entered name

            :param detailed_info: dictionary containing data about specific conversation
            :param format: ".txt" or ".csv"
            """
            result_list = []
            for part, msges in sorted(detailed_info["msg_count"].items(), key=lambda item: item[1], reverse=True):
                result_list.append([part, msges, detailed_info["msg_length"][part] / msges if msges != 0 else 0])

            if format == "csv":

                filename = simpledialog.askstring(title="Save to CSV",
                                                  prompt="Enter CSV filename (without .csv)")
                if filename is not None:
                    create_report(result_list, filename)
            elif format == "txt":
                filename = simpledialog.askstring(title="Save to TXT",
                                                  prompt="Enter TXT filename (without .txt)")
                if filename is not None:
                    with open(f"{os.curdir}/Files/{filename}.txt", "w+") as f:
                        f.write("{:30}\t|{:10}\t|{:5}\n".format("Participant", "Messages", "Average message length"))
                        f.write("-" * 72)
                        for row in result_list:
                            f.write("\n{:30}\t|{:10}\t|{:05.2f}".format(row[0], str(row[1]), row[2]))

        self.button_save_txt = Button(self.frame_buttons, text="Save txt", command=lambda: save_details(details, "txt"),
                                      width=10, bg="#0A353A",
                                      fg="white")
        self.button_save_csv = Button(self.frame_buttons, text="Save csv", command=lambda: save_details(details, "csv"),
                                      width=10, bg="#0A353A",
                                      fg="white")
        self.button_reactions = Button(self.frame_buttons, text="Reactions", bg="#0A353A", fg="white",
                                       command=lambda: ReactionsWindow(self, details["reactions"]))

        self.button_semantics = Button(self.frame_buttons, text="Semantics", bg="#0A353A", fg="white",
                                       command=lambda: EmotionsWindow(self, details["messages"]))

        self.button_save_txt.pack(side=LEFT, padx=40)
        self.button_save_csv.pack(side=LEFT)
        self.button_reactions.pack(side=LEFT, padx=40)
        self.button_semantics.pack(side=LEFT)

        Button(self.frame_buttons, text="Messages by month", bg="#0A353A", fg="white", font=("Calibri", 10),
               command=lambda: create_graph(details["msg_by_month"], "Messages per Month", "Messages")).pack(side=LEFT,
                                                                                                             padx=40)
        Button(self.frame_buttons, text="Avg response time", bg="#0A353A", fg="white", font=("Calibri", 10),
               command=lambda: create_graph(details["response"], "Average response time per Month", "Time [s]")).pack(
            side=LEFT)

        frame_header = Frame(self.frame_up, bg=tl.cget('bg'))
        frame_header.pack(side=BOTTOM, fill=X, expand=True, padx=20, pady=15)
        Label(frame_header, text="Participant", bg=frame_header.cget('bg'), font=("Century Gothic", 14)).pack(side=LEFT)
        Label(frame_header, text="Avg length", bg=frame_header.cget('bg'), font=("Century Gothic", 14), width=10,
              anchor=E).pack(side=RIGHT, padx=20)
        Label(frame_header, text="Messages", bg=frame_header.cget('bg'), font=("Century Gothic", 14), width=10,
              anchor=E).pack(side=RIGHT, padx=20)

        for part, msges in sorted(details["msg_count"].items(), key=lambda item: item[1], reverse=True):
            frame_participant = Frame(tl, bg=tl.cget('bg'))
            Label(frame_participant, text=part, bg=frame_participant.cget('bg'), fg="#3d3d3d",
                  font=("Century Gothic", 14)).pack(side=LEFT, padx=20)
            Label(frame_participant, text="{:05.2f}".format(
                details["msg_length"][part] / msges if msges != 0 else 0), bg=frame_participant.cget('bg'),
                  fg="#3d3d3d",
                  font=("Century Gothic", 14), width=10, anchor=E).pack(side=RIGHT, anchor=W, padx=20)

            Label(frame_participant, text=msges, bg=frame_participant.cget('bg'), fg="#3d3d3d",
                  font=("Century Gothic", 14), width=10, anchor=E).pack(side=RIGHT, padx=20)

            frame_participant.pack(side=TOP, fill=X, expand=True)


class ReactionsWindow(Toplevel):
    def __init__(self, master, reactions_list, **kw):
        super().__init__(master=master, **kw)
        self.configure(bg='white')
        """
        Creates Toplevel window containing 5 most used reactions by every participant

        :param reactions_list: dictionary with amounts of reactions used by every participant
        """
        self.title("Top 5 everyone's reactions")
        self.geometry("500x400+900+300")

        participant_frames = []

        varName = StringVar()

        def search_reactions():
            searched_name = varName.get()
            varName.set("")
            for frame in participant_frames:
                frame.pack_forget()
            for frame in filter(lambda a: searched_name in a.owner, participant_frames):
                frame.pack(side=TOP, anchor=W, padx=10)

        frame_header_search = Frame(self, bg=self.cget('bg'))
        frame_header_search.pack(side=TOP, expand=True, anchor=W)

        entry_participant_search = Entry(frame_header_search, bg=self.cget('bg'), textvariable=varName)
        entry_participant_search.pack(side=LEFT, expand=True, padx=10)

        button_participant_search = Button(frame_header_search, text="Search", bg=self.cget('bg'),
                                           command=search_reactions)
        button_participant_search.pack(side=LEFT, expand=True)

        scroll_reactions = ScrollableFrame(self, bg=self.cget('bg'))
        scroll_reactions.pack(side=BOTTOM, fill=BOTH, expand=True)

        for part, dict in reactions_list.items():
            result_frame = Frame(scroll_reactions.scrolled_frame, bg=self.cget('bg'))
            Label(result_frame, text=f"{part}:", bg=self.cget('bg')).pack(side=TOP, anchor=W)
            counter = 1
            for emote, number in dict.items():
                if counter == 6:
                    break
                Label(result_frame, font=("segoeui", 12), bg=self.cget('bg'),
                      text="{}.{} => {}".format(counter, emote.encode('raw_unicode_escape').decode('utf8'),
                                                number)).pack(side=TOP, anchor=W)
                counter += 1

            result_frame.owner = part
            participant_frames.append(result_frame)

            result_frame.pack(side=TOP, anchor=W, padx=10)


class EmotionsWindow(Toplevel):
    def __init__(self, master, messages, **kw):
        super().__init__(master=master, **kw)
        """
        Creates Toplevel window with percentage distribution of emotions in messages

        :param messages: dictionary containing all messages from all of conversation's participants
        """
        self.configure(bg='white')
        self.title("Emotions analysis")
        self.geometry("600x400+900+300")

        varName = StringVar()
        participant_frames = []
        analyzer = TextAnalyzer(False)

        def search_emotions():
            searched_name = varName.get()
            varName.set("")
            for frame in participant_frames:
                frame.pack_forget()
            for frame in filter(lambda a: searched_name in a.owner, participant_frames):
                frame.pack(side=TOP, anchor=W, padx=10)

        analyzer.load_from_file("model_final")  # File with generated model

        analyzer.best_k = create_model(analyzer)

        frame_header_search = Frame(self, bg=self.cget('bg'))
        frame_header_search.pack(side=TOP, expand=True, anchor=W)

        entry_participant_search = Entry(frame_header_search, bg=self.cget('bg'), textvariable=varName)
        entry_participant_search.pack(side=LEFT, expand=True, padx=10)

        button_participant_search = Button(frame_header_search, text="Search", bg=self.cget('bg'),
                                           command=search_emotions)
        button_participant_search.pack(side=LEFT, expand=True)

        scroll_semantics = ScrollableFrame(self, bg=self.cget('bg'))
        scroll_semantics.pack(side=BOTTOM, fill=BOTH, expand=True)

        for participant, messages in messages.items():
            result_frame = Frame(scroll_semantics.scrolled_frame, bg=self.cget('bg'))
            Label(result_frame, text=f"{participant}:", bg='white', font=("segoeui", 18)).pack(side=TOP, anchor=W,
                                                                                               pady=10)
            results = analyzer.analyze_many_messages(messages)
            total = sum(amount for _class, amount in results.items())
            result = {k: "{:05.2f}%".format((v / total) * 100) for k, v in
                      sorted(results.items(), key=lambda _class: _class[1], reverse=True)}
            for emotion, percent in result.items():
                emotion_frame = Frame(result_frame, bg=self.cget('bg'))
                Label(emotion_frame, font=("segoeui", 18), bg='white',
                      text="{}".format(emotion), width=10, anchor=W).pack(side=LEFT, anchor=W)
                Label(emotion_frame, font=("segoeui", 18), bg='white',
                      text="=> {}".format(percent)).pack(side=LEFT, padx=5, anchor=W)
                emotion_frame.pack(side=TOP, anchor=W)
            result_frame.pack(side=TOP, anchor=W, padx=10)

            result_frame.owner = participant
            participant_frames.append(result_frame)


class ScrollableFrame(Frame):
    """
    Class containing scrollable frame
    """

    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = Canvas(self, bg=self.cget('bg'))
        scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrolled_frame = Frame(self.canvas, bg=self.canvas.cget('bg'))

        self.scrolled_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrolled_frame, anchor=NW)
        self.scrolled_frame.bind("<Configure>", self.on_configure)
        self.canvas.bind('<Configure>', self.frame_width)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

    def frame_width(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def on_configure(self, event):
        # Set the scroll region to encompass the scrolled frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


if __name__ == "__main__":
    window = Tk()
    app = App(window)
