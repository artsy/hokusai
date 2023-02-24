import click
import pdb

def print_command_tree(click_command):
  """Print a tree of Click commands rooted at the given click_command"""
  tree = {}
  tree.update(build_tree(click_command))
  print_tree(tree)

def print_tree(tree):
  """Print Click command tree"""
  for cmdname, subtree in tree.items():
    if isinstance(tree[cmdname]['command'], click.core.Group):
      print_tree(tree[cmdname]['children'])
    else:
      print_command(tree[cmdname]['command'])

def print_command(click_command):
  """Print Click command name and its docstring"""
  print(f'{click_command.name} - {click_command.__doc__}')

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
