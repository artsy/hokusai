from textwrap import shorten

import click

def build_tree(click_command):
  """
  Return a tree of Click commands rooted at the given click_command.
  The tree is represented by a Dict. Each element of the Dict uses:
  - the name of the Click command/group as key
  - the Click command object as value, or in case of a Click group, a sub-Dict.
  """
  cmdname = click_command.name
  tree = {}
  tree[cmdname] = {}
  if isinstance(click_command, click.core.Group):
    tree[cmdname]['command'] = click_command
    tree[cmdname]['children'] = {}
    for cmd in click_command.commands.values():
      tree[cmdname]['children'].update(build_tree(cmd))
  else:
    tree[cmdname]['command'] = click_command
    tree[cmdname]['children'] = {}
  return tree

def print_command(click_command, last=False, prefix=''):
  """Print the name and docstring of the given Click command object"""
  if last:
    hanger = '└──'
  else:
    hanger = '├──'
  line = prefix + hanger + " " + click_command.name + " - " + shorten(click_command.help, 100, placeholder='...')
  print(line)

def print_command_tree(click_command):
  """Build and print a tree of Click commands rooted at the given click_command"""
  tree = {}
  tree.update(build_tree(click_command))
  print_tree(tree, level=1)

def print_tree(tree, level, prefix=''):
  """Print the given tree of Click commands"""
  num_items = len(tree)
  for i, cmdname in enumerate(sorted(tree.keys())):
    cmdobj = tree[cmdname]['command']
    children = tree[cmdname]['children']
    if i == num_items - 1:
      last = True
      next_level_prefix = prefix + '    '
    else:
      last = False
      next_level_prefix = prefix + '│   '
    print_command(cmdobj, last=last, prefix=prefix)
    print_tree(children, level=level+1, prefix=next_level_prefix)
