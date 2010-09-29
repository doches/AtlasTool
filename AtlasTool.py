#!/usr/bin/env python
import os
import pygame
import re
import sys
from pygame.locals import *
from optparse import OptionParser

parser = OptionParser(usage="AtlasTool is a utility for packing multiple images into a single OpenGL texture (a texture atlas).\n\nAtlasTool %prog [options]")
parser.add_option("-d","--dir",dest="dir",help="(REQUIRED) Path to a directory containing desired texture images.")
parser.add_option("-s","--surface",dest="surface_size",help="Size of the surface into which to render, of the form WIDTHxHEIGHT). Defaults to 512x512.",default="512x512")
parser.add_option("-o","--output",dest="output",help="Filename to use when saving the texture & atlas. Defaults to 'texture'",default="texture")

(options,parser) = parser.parse_args()

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

x = 0
y = 0
line_height = 0
fout = open(atlas_filename,"w")
for file in files:
  if re.search(r"(jpg|jpeg|png|gif|bmp|pcx|tga|tif|lbm|pbm|pgm|ppm|xpm)$",file):
    image = pygame.image.load(os.path.join(directory,file))
    file = file[0:file.rindex(".")]
    print file
    if x + image.get_width() > surfsize[0]:
      x = 0
      y += line_height
      line_height = 0
    surf.blit(image,(x,y))
    fout.write( file + "\t" + str(x) + "\t" + str(y) + "\t" + str(image.get_width()) + "\t" + str(image.get_height()) + "\n" )
    if y + image.get_height() > surfsize[1]:
      print file + " does not fit, try a larger surface size!"
    x += image.get_width()
    if image.get_height() > line_height:
      line_height = image.get_height()
pygame.image.save(surf,image_filename)
