################################################################################
#                                                                              # 
# Trees                                                                        # 
#                                                                              # 
# Author = Peter Ahrens                                                        #
# Version = 1.0                                                                #
# Date = October 24, 2012                                                      #
#                                                                              # 
################################################################################

import tkinter as tk
from tkinter import filedialog
from math import *
import copy


class Trunk(object):
    BRANCH_WIDTH = 2.0
    BRANCH_COLOR = "red"
    POINT_COLOR = "black"
    ROOT_COLOR = "blue"
    TIP_COLOR = "orange"
    NODE_SIZE = 5
    
    def __init__(self, canvas, editing=True):
        self.canvas = canvas
        self.editing = editing
        self.root_x = None
        self.root_y = None
        self.canvas_root = None
        self.tip_x = None
        self.tip_y = None
        self.canvas_tip = None
        self.points = []
        self.canvas_points = []
        self.branches = []
        self.canvas_branches = []
        self.offspring = []

    def draw_branch(self, branch):
        coords = [(int(branch[0]), int(branch[1])), (int(branch[2]), int(branch[3]))]
        line = self.canvas.create_line(coords, width=self.BRANCH_WIDTH, fill=self.BRANCH_COLOR)
        self.canvas_branches.append(line)
             
    def remove_branch(self,branch_id):
        try:
            i = self.canvas_branches.index(branch_id)
            self.canvas.delete(branch_id)
            self.canvas_branches.pop(i)
            self.branches.pop(i)
            return True
        except ValueError:
            return False

    def add_branch(self, x1, y1, x2, y2):
        self.branches.append((x1,y1,x2,y2))
        if self.editing:
            self.draw_branch((x1,y1,x2,y2))

    def make_circle(self, point, color):
        x = point[0]
        y = point[1]
        r = point[2]
        bbox = (int(x-r), int(y-r), int(x+r), int(y+r))
        return self.canvas.create_oval(bbox, fill=color, outline=color)
   
    def draw_point(self, point, color=POINT_COLOR):
        self.canvas_points.append(self.make_circle(point,color))

    def remove_point(self,point_id):
        try:
            i = self.canvas_points.index(point_id)
            self.canvas.delete(point_id)
            self.canvas_points.pop(i)
            self.points.pop(i)
            return True
        except ValueError:
            return False
        
    def add_point(self,x,y,radius):
        self.points.append((x,y,radius))
        self.draw_point((x,y,radius))
        
    def set_tip(self,x,y):
        if self.canvas_tip is not None:
            self.remove_tip()
        if self.editing:
            self.canvas_tip = self.make_circle((x,y,self.NODE_SIZE),self.TIP_COLOR)
        self.tip_x = x
        self.tip_y = y

    def remove_tip(self):
        self.canvas.delete(self.canvas_tip)
        self.canvas_tip = None
        self.tip_x = None
        self.tip_y = None

    def set_root(self,x,y):
        if self.canvas_root is not None:
            self.remove_root()
        if self.editing:
            self.canvas_root = self.make_circle((x,y,self.NODE_SIZE),self.ROOT_COLOR)
        self.root_x = x
        self.root_y = y

    def remove_root(self):
        self.canvas.delete(self.canvas_root)
        self.canvas_root = None
        self.root_x = None
        self.root_y = None

    def erase(self):
        self.remove_root()
        self.remove_tip()
        for branch in self.canvas_branches:
            self.canvas.delete(branch)
        self.canvas_branches = []
        self.branches = []
        for point in self.canvas_points:
            self.canvas.delete(point)
        self.canvas_points = []
        self.points = []
        self.erase_offspring()

    def erase_offspring(self):
        for child in self.offspring:
            child.erase()
        self.offspring = []
   
    def erase_object(self,object_id):
        if object_id == self.canvas_root:
            #self.remove_root() no removing roots!
            return True
        elif object_id == self.canvas_tip:
            #self.remove_tip() no removing tips!
            return True
        elif self.remove_branch(object_id):
            return True
        elif self.remove_point(object_id):
            return True
        else:
            for child in self.offspring:
                if child.erase_object(object_id):
                    return True
        return False

    def create_child(self, branch):
        child = Trunk(self.canvas, editing=False)
        child.set_root(branch[0], branch[1])
        child.set_tip(branch[2], branch[3])
        self_r = hypot(self.tip_x - self.root_x, self.tip_y - self.root_y)
        child_r = hypot(child.tip_x - child.root_x, child.tip_y - child.root_y)
        scale_factor = child_r/self_r
        delta_theta = atan2(child.tip_y-child.root_y, child.tip_x-child.root_x) - atan2(self.tip_y-self.root_y, self.tip_x-self.root_x)
        for point in self.points:
            r = hypot(point[0] - self.root_x, point[1] - self.root_y) * scale_factor
            theta = atan2(point[1] - self.root_y, point[0] - self.root_x) + delta_theta
            x = child.root_x + r * cos(theta)
            y = child.root_y + r * sin(theta)
            size = scale_factor * point[2]
            child.add_point(x,y,size)
        for branch in self.branches:
            r1 = hypot(branch[0] - self.root_x, branch[1] - self.root_y) * scale_factor
            theta1 = atan2(branch[1] - self.root_y, branch[0] - self.root_x) + delta_theta
            x1 = child.root_x + r1 * cos(theta1)
            y1 = child.root_y + r1 * sin(theta1)
            r2 = hypot(branch[2] - self.root_x, branch[3] - self.root_y) * scale_factor
            theta2 = atan2(branch[3] - self.root_y, branch[2] - self.root_x) + delta_theta
            x2 = child.root_x + r2 * cos(theta2)
            y2 = child.root_y + r2 * sin(theta2)
            child.add_branch(x1,y1,x2,y2)
        return child
   
    def grow(self,n):
        for branch in self.branches:
            child = self.create_child(branch)
            if n > 1:
                child.grow(n-1)
            self.offspring.append(child)

    def hide_edit_marks(self):
        if self.editing:
            for branch in self.canvas_branches:
                self.canvas.delete(branch)
            self.canvas_branches = []
            self.canvas.delete(self.canvas_tip)
            self.canvas_tip = None
            self.canvas.delete(self.canvas_root)
            self.canvas_root = None
            self.editing = False

    def show_edit_marks(self):
        if not self.editing:
            for branch in self.branches:
                self.draw_branch(branch)
            self.editing = True
            self.set_tip(self.tip_x, self.tip_y)
            self.set_root(self.root_x, self.root_y)

    def erase_all_redraw(self):
        self.canvas.delete(tk.ALL)
        self.offspring = []
        self.canvas_branches = []
        self.canvas_points = []
        self.canvas_tip = None
        self.canvas_root = None
        for point in self.points:
            self.draw_point(point)
        self.editing = False
            

class treedrawer(object):
    DEFAULT_WIDTH = 500
    DEFAULT_HEIGHT = 500
    DEFAULT_TIP_Y = .6
    UPPER_PEN_SIZE = 20
    UPPER_FRACTAL_LEVEL = 20
    ERASER_COLOR = "pink"
    GROW_COLOR = "green"
    
    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=tk.YES)

        buttons = tk.Frame(self.frame)

        l1 = tk.Label(buttons, text = "Pen Type:", justify=tk.LEFT)
        l1.pack(fill=tk.X)
        self.pen = tk.StringVar(buttons)
        self.pen.set("Select")
        self.pen.trace("w", self.pen_changed)
        self.old_pen = self.pen.get()
        o1 = tk.OptionMenu(buttons,self.pen,"Trunk","Branch","Tip","Root","Eraser","Grow")
        o1.config(width=10)
        o1.pack(fill=tk.X)
        self.branch_mark_x = None
        self.branch_mark_y = None
        self.branch_child = None
        l2 = tk.Label(buttons, text="Pen Size:", justify=tk.LEFT)
        l2.pack(fill=tk.X)
        self.pen_point = None
        self.pen_size = tk.IntVar(buttons)
        self.pen_size.trace("w", self.update_pen_preview)
        s1 = tk.Scale(buttons, var = self.pen_size, from_=1, to=self.UPPER_PEN_SIZE, orient=tk.HORIZONTAL)
        s1.pack(fill=tk.X)
        l3 = tk.Label(buttons, text="Preview:", justify=tk.LEFT)
        l3.pack(fill=tk.X)
        self.pen_preview = tk.Canvas(buttons, height=2*self.UPPER_PEN_SIZE+1, width=2*self.UPPER_PEN_SIZE+1, highlightthickness=0)
        self.pen_preview.pack()

        l4 = tk.Label(buttons, text="Depth:", justify=tk.LEFT)
        l4.pack(fill=tk.X)
        s2 = tk.Scale(buttons, from_=1, to=self.UPPER_FRACTAL_LEVEL, orient=tk.HORIZONTAL)
        s2.pack(fill=tk.X)
        self.s2 = s2
        b1 = tk.Button(buttons, text="Grow!", command = self.grow)
        b1.pack(fill=tk.X)
        b2 = tk.Button(buttons, text="Clear", command = self.reset)
        b2.pack(fill=tk.X)
        b3 = tk.Button(buttons, text="Save", command = self.save)
        b3.pack(fill=tk.X)

        buttons.pack(side=tk.LEFT)

        self.treespace = tk.Canvas(self.frame, width = self.DEFAULT_WIDTH, height = self.DEFAULT_HEIGHT, highlightthickness=0)
        self.treespace.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES)
        self.treespace.bind("<Button-1>", self.mouse_down)
        self.treespace.bind("<B1-Motion>", self.mouse_move)
        self.treespace.bind("<ButtonRelease-1>", self.mouse_up)

        self.trunk = Trunk(self.treespace)

    def save(self):
        formats = [('Encapsulated PostScript','*.eps'),]
        file_name = filedialog.asksaveasfilename(parent=root,filetypes=formats ,title="Save the image as...")
        if len(file_name ) > 0:
            self.treespace.postscript(file=file_name) # save canvas as encapsulated postscript

    def grow(self):
        if self.pen.get() != "Grow":
            self.pen.set("Grow")
            self.trunk.hide_edit_marks()
        self.trunk.erase_all_redraw()
        self.trunk.grow(self.s2.get())

    def setup_edit(self):
        self.trunk.erase_all_redraw()
        self.trunk.show_edit_marks()

    def setup_grow(self):
        self.trunk.erase_all_redraw()
        self.trunk.hide_edit_marks()

    def reset(self):
        self.trunk.erase()
        w = self.treespace.winfo_width()
        h = self.treespace.winfo_height()
        self.trunk.set_tip(w * 0.5, h * self.DEFAULT_TIP_Y) 
        self.trunk.set_root(w * 0.5, h - self.trunk.NODE_SIZE - 1)

    def pen_changed(self, *args):
        pen = self.pen.get()
        if self.old_pen == "Select":
            self.reset()
        if self.pen == "Grow":
            self.setup_grow()
        elif self.old_pen == "Grow":
            self.setup_edit()
        self.old_pen = pen
        self.update_pen_preview()

    def update_pen_preview(self, *args):
        pen = self.pen.get()
        if self.pen_point is not None:
            self.pen_preview.delete(self.pen_point)
            self.pen_point = None
        x = self.UPPER_PEN_SIZE
        y = self.UPPER_PEN_SIZE
        if pen == "Branch":
            self.pen_point = self.pen_preview.create_line([(0,0),(2*x, 2*y)], width=self.trunk.BRANCH_WIDTH, fill=self.trunk.BRANCH_COLOR)
        elif pen == "Trunk":
            r = self.pen_size.get()
            bbox = (int(x-r), int(y-r), int(x+r), int(y+r))
            self.pen_point = self.pen_preview.create_oval(bbox, fill=self.trunk.POINT_COLOR)
        elif pen == "Tip":
            r = self.trunk.NODE_SIZE
            bbox = (int(x-r), int(y-r), int(x+r), int(y+r))
            self.pen_point = self.pen_preview.create_oval(bbox, fill=self.trunk.TIP_COLOR, outline=self.trunk.TIP_COLOR)
        elif pen == "Root":
            r = self.trunk.NODE_SIZE
            bbox = (int(x-r), int(y-r), int(x+r), int(y+r))
            self.pen_point = self.pen_preview.create_oval(bbox, fill=self.trunk.ROOT_COLOR, outline=self.trunk.ROOT_COLOR)
        elif pen == "Eraser":
            r = self.pen_size.get()
            bbox = (int(x-r), int(y-r), int(x+r), int(y+r))
            self.pen_point = self.pen_preview.create_rectangle(bbox, fill=self.ERASER_COLOR, outline=self.ERASER_COLOR)
        elif pen == "Grow":
            r = self.UPPER_PEN_SIZE
            bbox = (int(x-r), int(y-r), int(x+r), int(y+r))
            self.pen_point = self.pen_preview.create_rectangle(bbox, fill=self.GROW_COLOR, outline=self.GROW_COLOR)

    def mouse_down(self,event):
        x = self.treespace.canvasx(event.x)
        y = self.treespace.canvasy(event.y)
        pen = self.pen.get()
        if pen == "Trunk":
            self.trunk.add_point(x,y,self.pen_size.get())
        elif pen == "Branch":
            self.branch_mark_x = x
            self.branch_mark_y = y
        elif pen == "Tip":
            self.trunk.set_tip(x,y)
        elif pen == "Root":
            self.trunk.set_root(x,y)
        elif pen == "Eraser":
            r = self.pen_size.get()
            for object_id in self.treespace.find_overlapping(x-r,y-r,x+r,y+r):
                self.trunk.erase_object(object_id)

    def mouse_move(self,event):
        x = self.treespace.canvasx(event.x)
        y = self.treespace.canvasx(event.y)
        pen = self.pen.get()
        if pen == "Trunk":
            self.trunk.add_point(x,y,self.pen_size.get())
        elif pen == "Branch":
            if self.branch_child is not None:
                self.branch_child.erase()
                self.branch_child = None
            self.branch_child = self.trunk.create_child((self.branch_mark_x, self.branch_mark_y, x, y))
        elif pen == "Tip":
            self.trunk.set_tip(x,y)
        elif pen == "Root":
            self.trunk.set_root(x,y)
        elif pen == "Eraser":
            r = self.pen_size.get()
            for object_id in self.treespace.find_overlapping(x-r,y-r,x+r,y+r):
                self.trunk.erase_object(object_id)

    def mouse_up(self,event):
        x = self.treespace.canvasx(event.x)
        y = self.treespace.canvasx(event.y)
        pen = self.pen.get()
        if pen == "Branch":
            if self.branch_child is not None:
                self.branch_child.erase()
                self.branch_child = None
            if self.branch_mark_x is not None:
                self.trunk.add_branch(self.branch_mark_x, self.branch_mark_y, x, y)
                self.branch_mark_x = None
                self.branch_mark_y = None

root = tk.Tk()
root.wm_title("Trees")
tree = treedrawer(root)
root.mainloop()

# Copyright (c) 2012, Peter Ahrens.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# * Neither the name of the copyright holder nor the
# names of its contributors may be used to endorse or promote products
# derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL PETER AHRENS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
