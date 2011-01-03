#!/usr/bin/env python
import os
import re
import sys
import random
from optparse import OptionParser

parser = OptionParser(usage="AtlasTool is a utility for packing multiple images into a single OpenGL texture (a texture atlas).\n\nAtlasTool %prog [options]")
parser.add_option("-d","--dir",dest="dir",help="(REQUIRED) Path to a directory containing desired texture images.")
parser.add_option("-s","--surface",dest="surface_size",help="Size of the surface into which to render, of the form WIDTHxHEIGHT). Defaults to 512x512.",default="512x512")
parser.add_option("-o","--output",dest="output",help="Filename to use when saving the texture & atlas. Defaults to 'texture'",default="texture")

(options,parser) = parser.parse_args()

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
    
    while len(rects) > 0:
      rect = rects.pop()
      smallest = available[0].size()
      best = available[0]
      for candidate in available:
        if candidate.w > rect.w and candidate.h > rect.h:
          if smallest == -1 or candidate.size() < smallest:
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
        print "Could not fit",rect.id

screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("AtlasTool")
pygame.init()

image_filename = options.output + ".png"
atlas_filename = options.output + ".atlas"
directory = options.dir
surfsize = options.surface_size.split("x")
surfsize = (int(surfsize[0]),int(surfsize[1]))

surf = pygame.surface.Surface(surfsize,SRCALPHA)
files = os.listdir(directory)
images = {}
rects = []
for file in files:
  if re.search(r"(jpg|jpeg|png|gif|bmp|pcx|tga|tif|lbm|pbm|pgm|ppm|xpm)$",file):
    image = pygame.image.load(os.path.join(directory,file))
    rects.append( [image.get_width(),image.get_height(),file])
    images[file] = image

packing = Packing(surfsize[0],surfsize[1],rects).assignments
fout = open(atlas_filename,"w")
for key in images:
  file = key[0:key.rindex(".")]
  if key in packing:
    rect = packing[key]
    image = images[key]
    c = random.randint(0,255)
#    pygame.draw.rect(surf,(c,c,c,20),pygame.Rect(rect.x,rect.y,rect.w,rect.h))
    surf.blit(image,(rect.x,rect.y))
    fout.write( file + "\t" + str(rect.x) + "\t" + str(rect.y) + "\t" + str(image.get_width()) + "\t" + str(image.get_height()) + "\n" )
pygame.image.save(surf,image_filename)
  
exit()