import importlib
import os
import stat

# hokusai.commands re-exports the setup function under the module's name
setup_cmd = importlib.import_module('hokusai.commands.setup')

REQUIRED_TEMPLATES = [
  'Dockerfile.j2',
  '.dockerignore.j2',
  'hokusai/build.yml.j2',
  'hokusai/development.yml.j2',
  'hokusai/test.yml.j2',
  'hokusai/staging.yml.j2',
  'hokusai/production.yml.j2'
]

def describe_setup():
  def it_keeps_the_executable_bit_on_copied_files(mocker, tmp_path):
    template_dir = tmp_path / 'templates'
    (template_dir / 'hokusai').mkdir(parents=True)
    for template in REQUIRED_TEMPLATES:
      (template_dir / template).write_text('')
    (template_dir / 'scripts').mkdir()
    script = template_dir / 'scripts' / 'run.sh'
    script.write_text('#!/bin/sh\n')
    script.chmod(0o755)

    project_dir = tmp_path / 'project'
    project_dir.mkdir()
    mocker.patch.object(setup_cmd, 'CWD', str(project_dir))
    mocker.patch.object(setup_cmd, 'config')
    mocker.patch.object(setup_cmd, 'ECR')

    setup_cmd.setup('foo', None, str(template_dir), [], False)

    mode = os.stat(project_dir / 'scripts' / 'run.sh').st_mode
    assert mode & stat.S_IXUSR
