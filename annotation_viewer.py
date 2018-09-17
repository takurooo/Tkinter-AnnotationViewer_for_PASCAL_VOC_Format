 #--------------------------------------------------------
 # import
 #--------------------------------------------------------
import os
import shutil
import glob
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkmsg
import tkinter.filedialog as tkfd
from utils.annotation_utils import PascalVOC_Reader
from utils.draw_utils import draw_result
import cv2
 #--------------------------------------------------------
 # defines
 #--------------------------------------------------------
MAIN_DISPLAY_SIZE = "900x800"

 #--------------------------------------------------------
 # functions
 #--------------------------------------------------------
class ImageViewer():
    CANVAS_WIDTH = 640
    CANVAS_HEIGHT = 640
    IMAGE_WIDTH = 640
    IMAGE_HEIGHT = 480

    def __init__(self, master):
        self.parent = master
        self.parent.title("ImageViewer")
        self.parent.resizable(width=tk.TRUE, height=tk.TRUE)
        self.parent.bind("<Left>", self.prev)
        self.parent.bind("<Right>", self.next)
        self.parent.bind("<Return>", self.move)

        self.init_menubar()
        self.init_imageviewer()

    def init_menubar(self):
        menubar = tk.Menu(self.parent)
        self.parent.configure(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Dir", underline=0, menu=file_menu)
        file_menu.add_command(label="Open", underline=0, command=self.open_dir)


    def init_imageviewer(self):
        self.image_paths = list() # image abs_paths
        self.annotaiones = dict() # annotationes data
        # dirs
        self.root_dir = None
        self.image_dir = None
        self.annotation_dir = None

        self.image_tk = None # showing tkimage
        self.image_idx = 0 # current image idex
        self.image_cnt = 0 # num of image
        self.image_cur_id = None # showing tkimage id

        # main frame
        self.mframe = tk.Frame(self.parent)
        self.mframe.pack(fill=tk.BOTH, expand=1)

        # image frame
        self.iframe = tk.Frame(self.mframe)
        self.iframe.pack()
        self.image_canvas = tk.Canvas(self.iframe, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT,cursor='plus')
        self.image_canvas.pack(pady=0, anchor=tk.N)

        # control frame
        self.cframe = tk.Frame(self.mframe)
        self.cframe.pack(side=tk.TOP, padx=5, pady=10)
        self.prev_button = ttk.Button(self.cframe, text="<<", width=10, command=self.prev)
        self.prev_button.pack(side = tk.LEFT, padx=5)
        self.next_button = ttk.Button(self.cframe, text=">>", width=10, command=self.next)
        self.next_button.pack(side = tk.LEFT, padx=5)

        # status frame
        self.sframe = tk.Frame(self.mframe)
        self.sframe.pack(side=tk.TOP, padx=5, pady=10)
        self.status_label = ttk.Label(self.sframe,
                                     text="{:3d}/{:3d}".format(0,0),
                                     width=10,
                                     anchor=tk.CENTER)
        self.status_label.pack(side = tk.LEFT, padx=5)
        self.imagenum_entry = ttk.Entry(self.sframe, width=5)
        self.imagenum_entry.insert(tk.END, "")
        self.imagenum_entry.pack(side=tk.LEFT, padx=5)
        self.skip_button = ttk.Button(self.sframe, text="SKIP", width=5, command=self.skip)
        self.skip_button.pack(side=tk.LEFT, padx=5)

        # check frame
        self.ckframe = tk.Frame(self.mframe)
        self.ckframe.pack(side=tk.TOP, padx=5, pady=10)
        self.check_button = ttk.Button(self.ckframe, text="MOVE", width=5, command=self.move)
        self.check_button.pack(side=tk.LEFT, padx=5)

    def delete(self):
        # delete str in entrybox.
        self.dir_entry.delete(0, tk.END)

    def prev(self, event=None):
        if self.image_cnt == 0:
            return
        if 0 < self.image_idx:
            self.image_idx -= 1
            self.show_image(self.image_idx)

    def next(self, event=None):
        if self.image_cnt == 0:
            return
        if self.image_idx < (self.image_cnt-1):
            self.image_idx += 1
            self.show_image(self.image_idx)

    def skip(self, event=None):
        if self.image_cnt == 0:
            return
        img_num = self.imagenum_entry.get()
        if img_num.isdecimal():
            img_idx = int(img_num) - 1
            if 0 <= img_idx and img_idx <= (self.image_cnt-1):
                self.image_idx = img_idx
                self.show_image(self.image_idx)

    def update_imagestatus(self):
        if self.image_cnt != 0:
            self.status_label.configure(text="{:3d}/{:3d}".format(self.image_idx+1,self.image_cnt))
        else:
            self.status_label.configure(text="{:3d}/{:3d}".format(0,0))

    def delete_image_from_list(self):
        if 0 < self.image_cnt:
            self.image_paths.pop(self.image_idx)
            self.image_cnt -= 1
            if 0 < self.image_cnt:
                self.image_idx = min(self.image_idx, self.image_cnt-1)
                self.show_image(self.image_idx)
            else:
                self.image_idx = 0
                if self.image_cur_id is not None:
                    self.image_canvas.delete(self.image_cur_id)
                    self.image_cur_id = None
                    self.update_imagestatus()

    def move(self, event=None):
        if 0 < self.image_cnt:
            if 0 <= self.image_idx and self.image_idx <= (self.image_cnt-1):
                dst_dir = os.path.join(self.root_dir, "_moved_image")
                os.makedirs(dst_dir, exist_ok=True)
                shutil.move(self.image_paths[self.image_idx], dst_dir)
                self.delete_image_from_list()

    def show_image(self, idx):
        DISP_X = 0
        DISP_Y = 0

        if idx < 0 or idx >= self.image_cnt:
            raise ValueError("imageidx invalid")

        # update cnavas size
        #self.image_canvas.config(width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)

        #-----------------------------
        # preprocess image
        #-----------------------------
        _image_path = self.image_paths[idx]
        image_cv = cv2.imread(_image_path)
        image_cv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
        img_height, img_width, _ = image_cv.shape

        # resize VGA
        if img_width < img_height: # portrait
            image_cv = cv2.resize(image_cv, (self.IMAGE_HEIGHT, self.IMAGE_WIDTH))
        else: # landscape
            image_cv = cv2.resize(image_cv, (self.IMAGE_WIDTH, self.IMAGE_HEIGHT))

        # add annotaion
        basefname, _ = os.path.splitext(os.path.basename(_image_path))
        objects = self.annotaiones.get(basefname, None)
        if objects:
            for object in objects:
                xmin, ymin, xmax, ymax = object.box
                xmin = int(xmin*self.IMAGE_WIDTH)
                ymin = int(ymin*self.IMAGE_HEIGHT)
                xmax = int(xmax*self.IMAGE_WIDTH)
                ymax = int(ymax*self.IMAGE_HEIGHT)
                draw_result(image_cv, object.classname, 0, (xmin, ymin, xmax, ymax))

        # update cnavas image
        image_pil = Image.fromarray(image_cv)
        self.image_tk = ImageTk.PhotoImage(image_pil)
        self.image_cur_id = self.image_canvas.create_image(DISP_X, DISP_Y,
                                                           image=self.image_tk,
                                                           anchor=tk.NW)

        # update status label
        self.update_imagestatus()

    def init_annotation(self, dir):
        self.annotaiones = dict()

        if dir == "":
            return
        if not os.path.exists(dir):
            return
        if not os.path.isdir(dir):
            return

        self.annotaiones = PascalVOC_Reader(dir).read()

    def open_dir(self):
        # set dirs
        self.root_dir = tkfd.askdirectory()
        self.image_dir = os.path.join(self.root_dir, "img")
        self.annotation_dir = os.path.join(self.root_dir, "annotation")

        if self.image_dir == "":
            return

        if not os.path.exists(self.image_dir):
            tkmsg.showwarning("Warning", message="{} doesn't exist.".format(self.image_dir))
            return

        if not os.path.isdir(self.image_dir):
            tkmsg.showwarning("Warning", message="{} isn't dir.".format(self.image_dir))
            return

        self.image_paths = list()
        accepted_ext = (".jpeg", '.jpg', '.png')
        for ext in accepted_ext:
            self.image_paths.extend(glob.glob(os.path.join(self.image_dir, "*"+ext)))


        image_cnt = len(self.image_paths)
        if image_cnt == 0:
            tkmsg.showwarning("Warning", message="image doesn't exist.")
            return

        self.image_idx = 0
        self.image_cnt = image_cnt

        self.init_annotation(self.annotation_dir)
        self.show_image(self.image_idx)


#--------------------------------------------------------
 # main
 #--------------------------------------------------------
if __name__ == '__main__':
    root = tk.Tk()
    ImageViewer(root)
    root.resizable(width=True, height=True)
    root.geometry(MAIN_DISPLAY_SIZE)
    root.mainloop()
