import textwrap

import click

class CommandTreeNode():
  """Represent a node in a tree of Click commands"""
  def __init__(self, click_command):
    self.click_command = click_command
    self.children = []

def build_tree(click_command):
  """Build a tree of CommandTreeNode starting from the given click_command"""
  node = CommandTreeNode(click_command)
  if isinstance(click_command, click.core.Group):
    node.children = [build_tree(cmd) for _, cmd in sorted(click_command.commands.items())]
  return node

def print_command_in_tree(click_command, last=False, prefix=''):
  """Print the name and docstring of the given Click command, as part of a tree output"""
  if last:
    hanger = '└──'
  else:
    hanger = '├──'
  line = prefix + hanger + " " + click_command.name
  if click_command.help:
    line += " - " + textwrap.shorten(click_command.help, 100, placeholder='...')
  print(line)

def print_command_tree(click_command):
  """Print all sub-commands of the given click_command, as a tree"""
  root = build_tree(click_command)
  print_tree(root, level=1)

def print_tree(start_node, level, prefix=''):
  """Print CommandTreeNode tree from the given start_node"""
  num_children = len(start_node.children)
  for i, node in enumerate(start_node.children):
    if i == num_children - 1:
      last = True
      next_level_prefix = prefix + '    '
    else:
      last = False
      next_level_prefix = prefix + '│   '
    print_command_in_tree(node.click_command, last=last, prefix=prefix)
    print_tree(node, level=level+1, prefix=next_level_prefix)
