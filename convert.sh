#!/bin/sh

########################
## using “convert” from ImageMagick to do ps convert into PNG
#########################


for INP in *.ps
do
echo $INP
newname=`basename $INP .ps`
convert -density 150 -geometry 100% $INP $newname.png
echo ” convert $INP to $newname.png completely”
done
echo ” process ended, please check your graphical files”

convert -delay 100 -loop 0 *.png loop.gif
