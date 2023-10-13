import os
import sys

import hokusai

from hokusai.lib.environment import cert_file_path, frozen, templates_dir_path


def describe_frozen():
  def describe_attribute_exists():
    def it_returns_value(monkeypatch):
      monkeypatch.setattr(sys, 'frozen', 'blah', raising=False)
      assert frozen() == 'blah'
  def describe_attribute_does_not_exist():
    def it_returns_false(monkeypatch):
      monkeypatch.delattr(sys, 'frozen', raising=False)
      assert frozen() == False

def describe_cert_file_path():
  def describe_frozen():
    def it_returns_meipass(monkeypatch):
      monkeypatch.setattr(sys, 'frozen', 'blah', raising=False)
      monkeypatch.setattr(sys, '_MEIPASS', 'boo', raising=False)
      assert cert_file_path() == 'boo/lib/cert.pem'
  def describe_thawed():
    def it_returns_none(monkeypatch):
      monkeypatch.delattr(sys, 'frozen', raising=False)
      assert cert_file_path() == None

def describe_templates_dir_path():
  def describe_frozen():
    def it_returns_meipass(monkeypatch):
      monkeypatch.setattr(sys, 'frozen', 'blah', raising=False)
      monkeypatch.setattr(sys, '_MEIPASS', 'boo', raising=False)
      assert templates_dir_path() == 'boo/hokusai_datas/templates'
  def describe_thawed():
    def it_returns_repo_dir(monkeypatch):
      monkeypatch.delattr(sys, 'frozen', raising=False)
      assert templates_dir_path() == os.path.dirname(hokusai.__file__) + '/templates'
