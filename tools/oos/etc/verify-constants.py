"""
Tool for verify the spec constants

This tool is used for verify if there is missed constants definitions in
spec_constants.yaml, to use this tool, you need to prepare a file includes
the list of projects, every line in the file should be "<pypi name>:<repo name>"
format.

"""

import yaml

PROJECTS_FILE = "projects"
spec_constants = yaml.safe_load(open('spec_constants.yaml'))

project_names = []
project_repos = []
for p in open(PROJECTS_FILE).readlines():
    if not p.strip():
        continue
    p_name, r_name = p.strip().split(':')
    project_names.append(p_name.strip())
    project_repos.append(r_name.strip())

des_missed = list(
    set(project_names) - set(spec_constants['pkg_description'].keys()))

pypi_repo_unmatched = []
for p_name, p_repo in zip(project_names, project_repos):
    if ((p_name in spec_constants['pypi2reponame'] and
         spec_constants['pypi2reponame'][p_name] == p_repo) or
            (p_name not in spec_constants['pypi2reponame'] and
             'python-' + p_name == p_repo)):
        continue
    pypi_repo_unmatched.append(p_name)

print("Projects which description missed in spec_constants.yaml: %s"
      % des_missed)
print("pypi<-->repo name unmatched in spec_constants.yaml: %s"
      % pypi_repo_unmatched)
