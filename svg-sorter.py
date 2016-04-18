#!/usr/bin/python
# -*- coding: utf-8 -*-

# this is rather quick and dirty and it only works on svgs with straight lines

def align_left(paths, mi):

  res = []
  for path in paths:
    res.append(path-mi)

  return res

def export_svg(fn, paths, w, h, line_width=0.1):

  from cairo import SVGSurface, Context

  s = SVGSurface(fn, w, h)
  c = Context(s)

  c.set_line_width(line_width)

  for path in paths:

    c.new_path()
    c.move_to(*path[0,:])
    for p in path[1:]:
      c.line_to(*p)
    c.stroke()

  c.save()

def get_mid(v):

  from numpy import array

  mi = v.min(axis=0).squeeze()
  ma = v.max(axis=0).squeeze()
  midx = mi[0]+ma[0]
  midy = mi[1]+ma[1]
  move = array([[midx,midy]])*0.5
  return mi, ma, move

def spatial_concat(paths, eps=1.e-9):

  from numpy.linalg import norm
  from numpy import row_stack

  res = []
  curr = paths[0]
  concats = 0
  for p in paths[1:]:
    if p.shape[0]<2:
      print('WARNING: path with only one vertex.')
      continue
    if norm(p[0,:]-curr[-1,:])<eps:
      curr = row_stack([curr, p[1:,:]])
      concats += 1
    else:
      res.append(curr)
      curr = p

  res.append(curr)

  print('concats: ', concats)
  print('original paths: ', len(paths))
  print('number after concatination: ', len(res))

  print()

  return res

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

def get_lines_from_svg(fn, out):

  from lxml import etree
  from numpy import array

  res = {}

  with open(fn, 'rb') as f:
    tree = etree.parse(f)
    root = tree.getroot()
    fields = root.findall('.//{http://www.w3.org/2000/svg}line')

    paths = []

    print('num fields', len(fields))

    for f in fields:

      x1 = f.xpath('@x1').pop()
      y1 = f.xpath('@y1').pop()
      x2 = f.xpath('@x2').pop()
      y2 = f.xpath('@y2').pop()

      p = array([[x1,y1], [x2,y2]], 'float')
      paths.append(p)

    return paths



def main(args, **argv):

  from numpy import row_stack

  fn = args.fn
  out = args.out

  # w = 1000
  # h = 1000

  paths = get_lines_from_svg(fn, out)
  mi, ma, move = get_mid(row_stack(paths))
  paths, _ = spatial_sort(paths)
  paths = spatial_concat(paths)
  paths = align_left(paths, mi)

  w, h = ma - mi
  export_svg(out, paths, w, h, line_width=1)
  # return

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

