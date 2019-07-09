class MockECR(object):
  @property
  def aws_account_id(self):
    return '12345678'

  @property
  def registry(self):
    return []

  @property
  def project_repo(self):
    return 'nginxdemos'

  def project_repo_exists(self):
    return True

  def create_project_repo(self):
    return True

  def get_login(self):
    return ''

  def get_image_by_tag(self, tag):
    return 'latest'

  @property
  def images(self):
    return []

  def tag_exists(self, tag):
    return True

  def find_git_sha1_image_tag(self, tag):
    return 'latest'

  def retag(self, tag, new_tag):
    pass
