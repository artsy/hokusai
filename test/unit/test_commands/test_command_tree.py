import click

from hokusai.commands.command_tree import build_tree, CommandTreeNode

def describe_build_tree():
  def it_builds_a_tree_that_matches_chain_of_groups_and_commands():
    @click.group
    def group():
      pass

    @group.command
    def command1():
      pass

    @group.command
    def command2():
      pass

    root = build_tree(group)
    assert root.click_command.name == 'group'
    expected_children = ['command1', 'command2']
    children = sorted([child.click_command.name for child in root.children])
    assert children == expected_children
