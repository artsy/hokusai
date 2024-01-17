import os
import subprocess


def describe_create():
  def it_creates():
    resp = subprocess.run(
      'hokusai staging create --filename hokusai/staging-hokusai-integration-test.yml.j2',
      capture_output=True,
      shell=True,
      text=True,
      timeout=10
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'deployment.apps/hokusai-sandbox-web created' in resp.stdout
