import os
import subprocess


def describe_setup():
  def it_creates_yml():
    resp = subprocess.run(
      'hokusai review_app setup a-review-app',
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
  def it_creates_deployment():
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
    assert 'deployment.apps/hokusai-integration-test-web created' in resp.stdout

def describe_list():
  def it_lists_review_app():
    resp = subprocess.run(
      'hokusai review_app list',
      capture_output=True,
      shell=True,
      text=True,
      timeout=10
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'a-review-app' in resp.stdout
