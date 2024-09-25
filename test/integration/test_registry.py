import os
import pytest
import subprocess

from subprocess import TimeoutExpired


@pytest.mark.order(310)
def describe_push():
  def it_pushes():
    resp = subprocess.run(
      'hokusai registry push --force --overwrite',
      capture_output=True,
      shell=True,
      text=True,
      timeout=60
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'Pushed hokusai_hokusai-integration-test:latest' in resp.stdout
