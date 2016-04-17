#!/usr/bin/python
# -*- coding: utf-8 -*-

# this is rather quick and dirty and it only works on svgs with straight lines


def spatial_sort(paths, init_rad=0.01):

  from numpy import array
  from numpy import zeros
  from numpy.linalg import norm
  from scipy.spatial import cKDTree as kdt

  num = len(paths)

  res = []

  unsorted = set(range(2*num))

  xs = zeros((2*num,2), 'float')
  x_path = zeros(2*num, 'int')

  for i, path in enumerate(paths):
    xs[i,:] = path[0,:]
    xs[num+i,:] = path[-1,:]

    x_path[i] = i
    x_path[num+i] = i

  tree = kdt(xs)

  count = 0
  pos = array([0,0],'float')

  order = []

  while count<num:

    rad = init_rad
    while True:

      near = tree.query_ball_point(pos, rad)
      cands = list(set(near).intersection(unsorted))
      if not cands:
        rad *= 2.0
        continue

      dst = norm(pos - xs[cands,:], axis=1)
      cp = dst.argmin()
      uns = cands[cp]
      break

    path_ind = x_path[uns]
    path = paths[path_ind]

    if uns>=num:
      res.append(path[::-1])
      pos = paths[path_ind][0,:]
      unsorted.remove(uns)
      unsorted.remove(uns-num)

    else:
      res.append(path)
      pos = paths[path_ind][-1,:]
      unsorted.remove(uns)
      unsorted.remove(uns+num)

    order.append(path_ind)

    count += 1

  return res, order

def do_sort(fn, out):

  from lxml import etree
  from numpy import array

  res = {}

  with open(fn, 'rb') as f:
    tree = etree.parse(f)
    root = tree.getroot()
    fields = root.findall('.//{http://www.w3.org/2000/svg}line')

    paths = []

    print('num fields', len(fields))

    parent = fields[0].getparent()

    for f in fields:

      f.getparent().remove(f)
      x1 = f.xpath('@x1').pop()
      y1 = f.xpath('@y1').pop()
      x2 = f.xpath('@x2').pop()
      y2 = f.xpath('@y2').pop()

      p = array([[x1,y1], [x2,y2]], 'float')
      paths.append(p)
    res, _ = spatial_sort(paths)

  for row in res:
    el = etree.Element(
      'line', **{'fill':'none', 'stroke':'#000000', 'stroke-linecap':'round',
        'stroke-linejoin':'round',
        'x1': str(row[0,0]),
        'y1': str(row[0,1]),
        'x2': str(row[1,0]),
        'y2': str(row[1,1]),
        }
    )
    parent.append(el)

  with open(out, 'w') as f:
      f.write(etree.tostring(root, pretty_print = True))


def main(args, **argv):

  # from cairo import SVGSurface, Context

  fn = args.fn
  out = args.out

  do_sort(fn, out)

  return

if __name__ == '__main__':

  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--fn',
    type=str,
    required=True
  )
  parser.add_argument(
    '--out',
    type=str,
    required=True
  )

  args = parser.parse_args()
  main(args)

