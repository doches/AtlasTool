#!/usr/bin/env python
import os
import re
import sys
import random
from optparse import OptionParser

parser = OptionParser(usage="AtlasTool is a utility for packing multiple images into a single OpenGL texture (a texture atlas).\n\nAtlasTool %prog [options]")
parser.add_option("-d","--dir",dest="dir",help="(REQUIRED) Path to a directory containing desired texture images.")
parser.add_option("-s","--surface",dest="surface_size",help="Size of the surface into which to render, of the form WIDTHxHEIGHT.",default="0x0")
parser.add_option("-o","--output",dest="output",help="Filename to use when saving the texture & atlas. Defaults to 'texture'",default="texture")
parser.add_option("-f","--fill",dest="debug",help="Fill individual rectangles on use for debugging.",default=False,action="store_true")
parser.add_option("-n","--no-spacing",dest="spacing",help="Do not add a 1-pixel space around all bounding boxes",default=False,action="store_true")

(options,parser) = parser.parse_args()

print options
if options.spacing:
	options.spacing = 0
else:
	options.spacing = 1

import pygame
from pygame.locals import *

class Rectangle:
  def __init__(self,x,y,w,h,id=False):
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    self.id = id
  
  def size(self):
    return self.h*self.w

def psort(a,b):
	return a[0]*a[1] < b[0]*b[1]

class Packing:
  def __init__(self,width,height,list):
    rects = []
    sorted = [[x[0]*x[1],x] for x in list]
    sorted.sort()
    for pair in sorted:
      rects.append( Rectangle(0,0,pair[1][0],pair[1][1],pair[1][2]) )
    available = [Rectangle(0,0,width,height)]
    
    self.assignments = {}
    self.valid = True
    
    while len(rects) > 0:
      rect = rects.pop()
      smallest = 0
      best = None
      for candidate in available:
        if candidate.w >= rect.w and candidate.h >= rect.h:
          if best == None or candidate.size() < smallest:
            smallest = candidate.size()
            best = candidate
      if best != None:
        available.remove(best)
        self.assignments[rect.id] = best
        for child in [Rectangle(best.x+rect.w,best.y+rect.h,best.w-rect.w,best.h-rect.h),
                      Rectangle(best.x,best.y+rect.h,rect.w,best.h-rect.h),
                      Rectangle(best.x+rect.w,best.y,best.w-rect.w,rect.h)]:
          available.append(child)
      else:
        print "Could not fit " + str(rect.id) + " in " + str(width) + "x" + str(height)
        self.valid = False
        break

screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("AtlasTool")
pygame.init()

directory = options.dir

files = os.listdir(directory)
images = {}
rects = []
for file in files:
  if re.search(r"(jpg|jpeg|png|gif|bmp|pcx|tga|lbm|pbm|pgm|ppm|xpm)$",file):
    image = pygame.image.load(os.path.join(directory,file))
    rects.append( [image.get_width()+options.spacing,image.get_height()+options.spacing,file])
    images[file] = image

valid_sizes = [(256,256),(512,256),(512,512),(1024,512),(1024,1024),(2048,1024),(1024,2048),(2048,2048)]
size_index = 0

image_filename = options.output + ".png"
atlas_filename = options.output + ".atlas"
packing = False
if (options.surface_size != "0x0"):
	surfsize = options.surface_size.split("x")
	surfsize = (int(surfsize[0]),int(surfsize[1]))
	packing = Packing(surfsize[0],surfsize[1],rects).assignments
else:
	surfsize = valid_sizes[size_index]
	packing = Packing(surfsize[0],surfsize[1],rects)
	while packing.valid != True:
		size_index += 1
		surfsize = valid_sizes[size_index]
		packing = Packing(surfsize[0],surfsize[1],rects)
	packing = packing.assignments
	print "Packing into " + str(valid_sizes[size_index][0]) + "x" + str(valid_sizes[size_index][1])

surf = pygame.surface.Surface(surfsize,SRCALPHA)

fout = open(atlas_filename,"w")
# Save texture size as special 'resolution' key
fout.write("resolution\t0\t0\t" + str(surfsize[0]) + "\t" + str(surfsize[1]) + "\n")
for key in images:
  file = key[0:key.rindex(".")]
  if key in packing:
    rect = packing[key]
    image = images[key]
    if options.debug:
      r = random.randint(0,255)
      g = random.randint(0,255)
      b = random.randint(0,255)
      pygame.draw.rect(surf,(r,g,b,255),pygame.Rect(rect.x,rect.y,rect.w,rect.h))
    surf.blit(image,(rect.x,rect.y))
    fout.write( file + "\t" + str(rect.x) + "\t" + str(rect.y) + "\t" + str(image.get_width()) + "\t" + str(image.get_height()) + "\n" )
pygame.image.save(surf,image_filename)
  
exit()
