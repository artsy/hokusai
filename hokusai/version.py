# determine app version
try:
  # Import from 'hokusai/_version.py' file.
  # The file is created by 'python -m setuptools_scm' (see Makefile) during builds and bundled into artifacts.
  # The file is not version controlled.
  #
  # 'version' is a version guessed by 'setuptools_scm',based on local Git state (latest tag, commits since that tag, the branch checked out).
  # Say the latest tag is v1.0.3, and the branch has one or more commits ahead of that tag, likely the case for 'main' branch,
  # 'setuptools_scm' will guess a dev version preceding the next canonical release, such as '1.0.4.dev30+gdf56449'.
  # The 'df56449' portion is the abbrviated Git commit hash, useful for associating a beta release to its commit.
  #
  # To release a canonical version (e.g. v1.0.4, v1.1.0, v2.0.0), create a tag for the desired version.
  # 'setuptools_scm' will set 'version' to exactly that version, meaning it won't guess.
  # CircleCI 'release' builds are configured to create such tags,
  # based on the RELEASE_VERSION file which is bumped manually when preparing a release.
  from hokusai._version import version
  VERSION = version
except ImportError:
  # mainly for local development when setuptools_scm command is likely not run
  VERSION = 'v0.0.0'
