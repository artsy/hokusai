import os

from hokusai.lib.exceptions import HokusaiError

class TemplateSelector(object):
  def get(self, path):
    _path_root, _file_ext = os.path.splitext(path)

    if _file_ext:
      if not os.path.isfile(path):
        raise HokusaiError("File %s does not exist." % path)
      return path

    if os.path.isfile(path + '.yml.j2'):
      return path + '.yml.j2'
    if os.path.isfile(path + '.yaml.j2'):
      return path + '.yaml.j2'
    if os.path.isfile(path + '.yml'):
      return path + '.yml'
    if os.path.isfile(path + '.yaml'):
      return path + '.yaml'

    raise HokusaiError("No Yaml or Jinja templates found for %s" % os.path.basename(path))
