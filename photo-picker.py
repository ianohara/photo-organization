#!/usr/bin/env python2.7
################################################################################
#
#  Utility for going through a series of images and only copy the ones you
#  want.  This is useful when dumping all of the images from eg: a digital
#  camera when you really only want to keep a few of the 20000 photos you
#  hammered out.
#
################################################################################
from __future__ import print_function

from PIL import ImageTk, Image
from tkMessageBox import showinfo
import argparse, os, shutil, sys, timer
import Tkinter as Tk

def usage(msg=''):
    ap.print_help()
    if len(msg):
        print("Usage Message: ", msg)
        sys.exit(1)
    sys.exit(0)

def verbose(*a, **kwargs):
    if args.verbose:
        print("[%5.3f]" % time.time(), *a, **kwargs)

def exit_success():
    showinfo("Successfully completed!",
             "There are no more images to keep/pass. Kept images writen to '%s'." % args.out_dir)
    sys.exit(0)

def open_image(fname):
    assert os.path.isfile(fname)
    c.image = ImageTk.PhotoImage(file=fname)
    c.create_image(0,0, anchor=Tk.NW, image=c.image)
    c.configure(c, scrollregion=(0,0,c.image.width(), c.image.height()))

def next_image():
    global current_image
    if not len(image_paths):
        exit_success()
    current_image = image_paths.pop()
    verbose("next_image:")
    verbose("  current_image=", current_image)
    open_image(current_image)

def keep_image():
    do_it = True
    verbose("Keep image:")
    verbose("  current_image=", current_image)
    keep_path = os.path.join(args.out_dir, os.path.basename(current_image))
    verbose("  keep_path=", keep_path)
    if os.path.isfile(keep_path):
        ans = askquestion("Image already exists in keep dest.",
                          "The image '%s' already exists.  Overwrite it?" % keep_path)
        if ans != "yes": do_it = False

    if do_it:
        verbose("Keeping current image: ", current_image)
        shutil.copyfile(current_image, keep_path)
    else:
        verbose("Wanted to keep image '%s' but it already exists at the destination, so skipping..." % current_image)

    next_image()

def pass_image():
    verbose("Passing on current image: ", current_image)
    next_image()

ap = argparse.ArgumentParser(description="Look for all images in a directory and copy selected images to a new directory for 'keeping'.  The originals are left untouched.")
ap.add_argument("dir", type=str, help="The directory to scan for source images.")
ap.add_argument("--out_dir", "-o", type=str, default="/tmp/kept_photos", help="The output directory in which kept photos should be put.")
ap.add_argument("--types", nargs="+", default=["png"], type=str, help="File types to consider as images (eg: 'png', 'jpg', etc)")
ap.add_argument("--verbose", action="store_true", help="Turn on verbose output.")

args = ap.parse_args()
image_paths = []

if not os.path.isdir(args.dir):
    usage("Input directory '%s' does not exist." % args.dir)

if not os.path.isdir(args.out_dir):
    try:
        os.mkdir(args.out_dir)
    except OSError as e:
        usage("Could not create '%s' because: %s" % (args.out_dir, str(e)))

def image_list_builder(_, dirs, files):
    for f in files:
        if any([f.endswith(t) for t in args.types]):
            image_paths.append(os.path.abspath(f))

os.path.walk(args.dir, image_list_builder, None)

verbose("Found images: ")
verbose("\n".join([i for i in image_paths]))


current_image=None

r = Tk.Tk() # "root"
r.config(bg="White")
rtit = r.title("Photo Picker")
rw_max = r.winfo_screenwidth()
rw_min = 800
rh_max = r.winfo_screenheight()
rh_min = 600

r.minsize(rw_min, rh_min)
r.maxsize(rw_max, rh_max)

c = Tk.Canvas(r, width=rw_min, height=rh_min)
c.pack(side=Tk.TOP)
b_keep = Tk.Button(r, text="Keep", command=keep_image)
b_keep.pack(side=Tk.BOTTOM)
b_pass = Tk.Button(r, text="Pass", command=pass_image)
b_pass.pack(side=Tk.BOTTOM)

next_image()

Tk.mainloop()
