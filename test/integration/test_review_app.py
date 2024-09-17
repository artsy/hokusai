import os
import pytest
import subprocess


@pytest.mark.order(1010)
def describe_setup():
  def it_sets_up():
    subprocess.run(
      'hokusai staging create',
      capture_output=True,
      shell=True,
      text=True,
      timeout=10
    )
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
    assert 'namespace/a-review-app created' in resp.stdout
    assert 'Copying hokusai-integration-test-environment ConfigMap to a-review-app namespace' in resp.stdout
    assert 'configmap/hokusai-integration-test-environment created' in resp.stdout
#    assert 'serviceaccount/a-review-app created' in resp.stdout

@pytest.mark.order(1020)
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

@pytest.mark.order(1030)
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

@pytest.mark.order(1040)
def describe_delete():
  def it_deletes_review_app():
    resp = subprocess.run(
      'hokusai review_app delete a-review-app',
      capture_output=True,
      shell=True,
      text=True,
      timeout=10
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'Deleted Kubernetes environment' in resp.stdout
    assert 'namespace "a-review-app" deleted' in resp.stdout
