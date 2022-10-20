#!/usr/bin/env python3

from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.shortcuts import set_title
from tkinter import messagebox
from ttkbootstrap import *
from ttkbootstrap import Window
from ttkbootstrap.tooltip import ToolTip
from prompt_toolkit import prompt, HTML, print_formatted_text
import prompt_toolkit.output.win32
from qrcode.exceptions import DataOverflowError
import qrcode # pip3 install qrcode[pil]
import pyqrcode
import random
import sys
import os.path

from icon import icon as icon_data


def GUI():
    qrer = Window(themename="cosmo")
    qrer.title("QRer | 1.0.0")
    qrer.resizable(False, False)
    icon = PhotoImage(data=icon_data)
    qrer.call('wm', 'iconphoto', qrer._w, icon)

    Label(qrer, text="Data:").pack(side='top', padx=3)

    data_frame = Frame(qrer)
    data_frame.pack(side='top', expand=True, fill='both', padx=3, pady=3)

    data_scrollBar = Scrollbar(data_frame, bootstyle='rounded')
    data_scrollBar.pack(side='right', fill='y')

    data = Text(data_frame, yscrollcommand=data_scrollBar.set, highlightbackground="#00ddff")
    data.pack(expand=True, fill='both', side='left')
    data_scrollBar.configure(command=data.yview)

    qr_options_frame = Frame(qrer)
    qr_options_frame.pack(side='top')

    qr_box_sizing_Var = IntVar(value=16)
    qr_box_sizing = Spinbox(qr_options_frame, from_=0, to=100, textvariable=qr_box_sizing_Var)
    qr_box_sizing.pack(side='left', padx=5, pady=10)
    ToolTip(qr_box_sizing, "Box Sizing")

    qr_box_border_Var = IntVar(value=1)
    qr_box_border = Spinbox(qr_options_frame, from_=0, to=100, textvariable=qr_box_border_Var)
    qr_box_border.pack(side='left', padx=10, pady=10)
    ToolTip(qr_box_border, "Box Border")

    qr_data_optimize_Var = IntVar(value=20)
    qr_data_optimize = Spinbox(qr_options_frame, from_=0, to=100, textvariable=qr_data_optimize_Var)
    qr_data_optimize.pack(side='left', padx=10, pady=10)
    ToolTip(qr_data_optimize, "Data Optimize (Data chunks to find more compressed modes of at least this length)", wraplength=150)

    qr_fitVar = BooleanVar(value=True)
    qr_fit = Checkbutton(qr_options_frame, text="fit", variable=qr_fitVar, takefocus=False)
    qr_fit.pack(side='left', padx=5, pady=10)
    ToolTip(qr_fit, "Find the best fit for the data to avoid (data overflow errors)", wraplength=150)

    action_frame = Frame(qrer)
    action_frame.pack(side='bottom', expand=True, fill='x')

    def Save():
        qr_content = data.get(1.0, 'end').strip()
        filename = file_name.get()
        if len(qr_content.replace(" ", "")) > 0 and filename and not os.path.exists(filename) or qr_overwriteVar.get():
            try:
                qr = qrcode.QRCode(version=1, box_size=qr_box_sizing_Var.get(), border=qr_box_border_Var.get(), error_correction=qrcode.constants.ERROR_CORRECT_H)
                qr.add_data(data=qr_content, optimize=qr_data_optimize_Var.get())
                qr.make(fit=qr_fitVar.get())
                image = qr.make_image(fill_color="black", back_color="white")
                image.save(filename)
                messagebox.showinfo(title="done!", message=f"{filename} made successfully and {len(qr_content)} character was writen to it.")
            except DataOverflowError:
                messagebox.showerror(title="failed!", message=f"{filename} can't take {len(qr_content)} character long.")
                data.focus_set()
        validate_path()

    generate_btn = Button(action_frame, text="generate", cursor="hand2", takefocus=False, command=lambda :Save())
    generate_btn.pack(side='right', pady=3, padx=3)

    Label(action_frame, text="File:").pack(side='left', padx=5)

    file_name = Entry(action_frame)

    def validate_path():
        filename = file_name.get()
        if os.path.exists(filename) == False:
            file_name.config(bootstyle='primary')
        else:
            file_name.config(bootstyle='danger')

    qr_overwriteVar = BooleanVar(value=False)
    qr_overwrite = Checkbutton(action_frame, text="overwrite", bootstyle='toolbutton-danger', cursor="hand2", variable=qr_overwriteVar, takefocus=False)
    qr_overwrite.pack(side='right', padx=5, pady=10)
    ToolTip(qr_overwrite, "Overwrite exist file")

    file_name.bind("<KeyPress>", lambda a:validate_path())
    file_name.bind("<KeyRelease>", lambda a:validate_path())
    data.bind("<KeyPress>", lambda a:validate_path())
    data.bind("<KeyRelease>", lambda a:validate_path())
    file_name.pack(side='left', fill='x', expand=True, pady=3, padx=3)
    qrer.mainloop()

def CLI():
    try:
        placeholder_msg = "Press " \
                          "<style fg='navy'>Enter</style>/<style fg='navy'>Return</style> to go new line, When finished press " \
                          "<style fg='navy'>Esc</style>" \
                          "/" \
                          "<style fg='navy'>R-Alt</style>" \
                          "<style fg='#ffffff'>+</style>" \
                          "<style fg='navy'>Enter</style>" \
                          "/<style fg='navy'>Return</style>"
        placeholder_color = "#3d2929" # gray
        line_number_color = "#ffffff" # white
        wrapline_char = "|" # should be one char only
        max_line_number = 999 # after these lines padding will start make no sense
        padding = " " * len(str(max_line_number)) # padding to make terminal line text editor

        def prompt_continuation(width, line_number, wrap_count):
            """
            The continuation: display line numbers and '->' before soft wraps.
            Notice that we can return any kind of formatted text from here.
            The prompt continuation doesn't have to be the same width as the prompt
            which is displayed before the first line, but in this example we choose to
            align them. The `width` input that we receive here represents the width of
            the prompt.
            """
            if wrap_count > 0: # if text is long enough to break out of the screen
                return padding + wrapline_char + (" " * len(str(line_number + 1)))
            else: # if enter pressed (for newline)
                text = (" %i " % (line_number + 1)).rjust(width)
                return HTML(f"<strong fg='{line_number_color}'>%s</strong>") % text

        content = prompt(message=padding + "1 ", include_default_pygments_style=True, cursor=CursorShape.BLINKING_BEAM, complete_in_thread=True, complete_while_typing=True, wrap_lines=True, validate_while_typing=True, enable_suspend=True, enable_history_search=True, search_ignore_case=True, multiline=True, prompt_continuation=prompt_continuation, mouse_support=True, placeholder=HTML(f"<style fg='{placeholder_color}'>{placeholder_msg}</style>"))
        set_title("QRer | 1.0.0")

        if len(content.replace(" ", "")) > 0:
            text = pyqrcode.create(content=content, error="Q")
            print(text.terminal(quiet_zone=1))


            rand = str(random.randint(1000000000, 9999999999))
            # save png
            filename = rand + ".png"
            text.png(file=filename)
            print(f"Saved to: {filename}")
    except KeyboardInterrupt:
        pass
    except prompt_toolkit.output.win32.NoConsoleScreenBufferError:
        pass
    except Exception as error:
        print_formatted_text(HTML(str(error)))

if '__main__' == __name__:
    args = sys.argv
    if "-c" in args or "--cli" in args:
        CLI()
    else:
        GUI()