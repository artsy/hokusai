import click
import pdb
from textwrap import dedent, wrap, fill, shorten, indent

def print_command_tree(click_command):
  """Print a tree of Click commands rooted at the given click_command"""
  tree = {}
  tree.update(build_tree(click_command))
  print_tree(tree, level=1)

def print_tree(tree, level):
  """Print Click command tree"""
  num_items = len(tree)
  for i, (cmdname, _) in enumerate(sorted(tree.items())):
    if i == num_items - 1:
      print_command(tree[cmdname]['command'], indent=level, last=True)
    else:
      print_command(tree[cmdname]['command'], indent=level, last=False)
    print_tree(tree[cmdname]['children'], level=level+1)

def print_command(command, indent, last):
  """Print Click command name and its docstring"""
  if last:
    padding = '      ' * (indent-1) + '└────'
  else:
    padding = '      ' * (indent-1) + '├────'

  print(padding, command.name, "-", end=' ')
  print(shorten(command.help, 100, placeholder='...'))

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
