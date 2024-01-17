import os
import subprocess


def describe_setup():
  def it_setups():
    resp = subprocess.run(
      'hokusai review_app setup --source-file hokusai/staging-hokusai-integration-test.yml.j2 a-review-app',
      capture_output=True,
      shell=True,
      text=True,
      timeout=10
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'Created hokusai/a-review-app.yml' in resp.stdout

def describe_create():
  def it_creates():
    subprocess.run(
      'hokusai registry push --force --skip-latest --tag a-review-app',
      shell=True,
      text=True,
      timeout=30
    )
    resp = subprocess.run(
      'hokusai review_app create a-review-app',
      capture_output=True,
      shell=True,
      text=True,
      timeout=10
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'deployment.apps/hokusai-sandbox-web created' in resp.stdout
