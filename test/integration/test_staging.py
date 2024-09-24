import os
import pytest
import subprocess

from subprocess import TimeoutExpired

@pytest.mark.order(500)
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

@pytest.mark.order(510)
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

@pytest.mark.order(520)
def describe_update():
  def it_reports_no_changes():
    resp = subprocess.run(
      'hokusai staging update --skip-checks',
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

@pytest.mark.order(530)
def describe_refresh():
  def it_reports_success():
    resp = subprocess.run(
      'hokusai staging refresh',
      capture_output=True,
      shell=True,
      text=True,
      timeout=30
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'Refreshing hokusai-integration-test-web' in resp.stdout
    assert 'Waiting for refresh to complete' in resp.stdout
    assert 'Waiting for deployment "hokusai-integration-test-web" rollout to finish' in resp.stdout
    assert 'deployment "hokusai-integration-test-web" successfully rolled out' in resp.stdout

@pytest.mark.order(1510)
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
