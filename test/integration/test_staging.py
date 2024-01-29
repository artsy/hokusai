import os
import pytest
import subprocess

from subprocess import TimeoutExpired


def describe_create():
  def it_reports_created():
    subprocess.run(
      'hokusai registry push --force',
      shell=True,
      text=True,
      timeout=30
    )
    resp = subprocess.run(
      'hokusai staging create',
      capture_output=True,
      shell=True,
      text=True,
      timeout=10
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'Created configmap hokusai-integration-test-environment' in resp.stdout
    assert 'deployment.apps/hokusai-integration-test-web created' in resp.stdout
    assert 'service/hokusai-integration-test-web created' in resp.stdout
    assert 'Created Kubernetes environment' in resp.stdout

def describe_status():
  def it_shows_resources():
    resp = subprocess.run(
      'hokusai staging status',
      capture_output=True,
      shell=True,
      text=True,
      timeout=10
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'Resources' in resp.stdout
    assert 'deployment.apps/hokusai-integration-test-web' in resp.stdout
    assert 'service/hokusai-integration-test-web' in resp.stdout
    assert 'Pods' in resp.stdout

def describe_update():
  def it_reports_no_changes():
    resp = subprocess.run(
      'hokusai staging update',
      capture_output=True,
      shell=True,
      text=True,
      timeout=10
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'deployment.apps/hokusai-integration-test-web unchanged' in resp.stdout
    assert 'service/hokusai-integration-test-web unchanged' in resp.stdout
    assert 'Updated Kubernetes environment' in resp.stdout

def describe_refresh():
  def it_times_out():
    # expect timeout due to minikube lacking ECR image pull permission
    with pytest.raises(TimeoutExpired):
      resp = subprocess.run(
        'hokusai staging refresh',
        capture_output=True,
        shell=True,
        text=True,
        timeout=10
      )
      if resp.returncode != -9:
        print(resp.stderr)
      assert resp.returncode == -9
      assert 'Refreshing hokusai-integration-test-web' in resp.stdout
      assert 'Waiting for refresh to complete' in resp.stdout
      assert 'Waiting for deployment "hokusai-integration-test-web" rollout to finish' in resp.stdout

def describe_delete():
  def it_reports_deleted():
    resp = subprocess.run(
      'hokusai staging delete',
      capture_output=True,
      shell=True,
      text=True,
      timeout=10
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'deployment.apps "hokusai-integration-test-web" deleted' in resp.stdout
    assert 'hokusai-integration-test-web" deleted' in resp.stdout
    assert 'Deleted configmap hokusai-integration-test-environment' in resp.stdout
    assert 'Deleted Kubernetes environment' in resp.stdout
