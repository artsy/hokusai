import click

def print_command_tree(click_command):
  """Print a tree of Click commands rooted at the given click_command"""
  tree = {}
  tree.update(build_tree(click_command))
  print(tree)

def build_tree(click_command):
  """
  Return a tree of Click commands rooted at the given click_command.
  The tree is represented by a Dict. Each element of the Dict uses:
  - the name of the Click command/group as key
  - the Click command object as value, or in case of a Click group, a sub-Dict.
  """
  cmdname = click_command.name
  tree = {}
  if isinstance(click_command, click.core.Group):
    tree[cmdname] = {}
    for cmd in click_command.commands.values():
      tree[cmdname].update(build_tree(cmd))
  else:
    tree[cmdname] = click_command
  return tree
