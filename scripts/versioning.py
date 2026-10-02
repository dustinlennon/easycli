# script to produce an up-to-date dependency entry, one based
# on Pipfile/Pipfile.lock, to pyproject.toml

import jinja2
import json
import sys
import textwrap
import tomllib

def template_loader(name):
  if name == 'packages':
    template = textwrap.dedent(
      """
      dependencies = [
        {%- for pkg_name, pkg_version in versioned_packages.items() %}
        '{{pkg_name}} ({{pkg_version}})'
        {{- ", " if not loop.last else "" }} 
        {%- endfor %}
      ]
      """
    ).strip()
  elif name == 'dev-packages':
    template = textwrap.dedent(
      """
      [dependency-groups]
      dev = [
        {%- for pkg_name, pkg_version in versioned_packages.items() %}
        '{{pkg_name}} ({{pkg_version}})'
        {{- ", " if not loop.last else "" }} 
        {%- endfor %}
      ]
      """
    ).strip()
  else:
    template = None

  return template

j2env = jinja2.Environment(
  loader = jinja2.FunctionLoader(template_loader)
)

#
# > print_formatted_list
#
def print_formatted_list(
    pipfile_section_name: str,
    lock_section_name: str
  ) -> str:
  versioned_packages = {}
  packages  = pipfile.get(pipfile_section_name, {})
  for package_name, config in packages.items():
    if isinstance(config, str) and config == '*':
      versioned_packages[package_name] = lock[lock_section_name][package_name]['version']

  print(
    j2env
      .get_template(pipfile_section_name)
      .render(versioned_packages = versioned_packages)
  )
  print()

#
# > __main__
#
if __name__ == '__main__':
  with open('Pipfile', 'rb') as fp:
    pipfile = tomllib.load(fp)

  with open('Pipfile.lock') as fp:
    lock = json.load(fp)

  print("Pipfile.lock versions for pyproject.toml", file = sys.stderr)
  print_formatted_list('packages', 'default')
  print_formatted_list('dev-packages', 'develop')
