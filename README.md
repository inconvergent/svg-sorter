# svg-sorter

Spatially sorts all lines in a svg, and creates new svg that is reasonably efficient for plotting.

Note that it currently ignores all svg elements that are not lines, including paths. 

Usage 

    svg-sorter.py --fn file.svg --out result.svg
