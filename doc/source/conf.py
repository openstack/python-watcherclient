# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.viewcode',
              'sphinxcontrib.apidoc',
              'openstackdocstheme',
             ]
# autodoc generation is a bit aggressive and a nuisance when doing heavy
# text edit cycles.
# execute "export SPHINX_DEBUG=1" in your terminal to disable

# sphinxcontrib.apidoc options
apidoc_module_dir = '../../watcherclient'
apidoc_output_dir = 'reference/api'
apidoc_excluded_paths = [
    'tests/*']
apidoc_separate_modules = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'python-watcherclient'
copyright = u'OpenStack Foundation'

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ['watcherclient.']

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'native'

# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages. Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
# html_theme_path = ["."]
# html_theme = '_theme'
# html_static_path = ['_static']
html_theme = 'openstackdocs'
# html_theme_path = [openstackdocstheme.get_html_theme_path()]

# Output file base name for HTML help builder.
htmlhelp_basename = '%sdoc' % project


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
    (
        'index',
        '%s.tex' % project,
        u'%s Documentation' % project,
        u'OpenStack Foundation', 'manual'
    ),
]

# Disable usage of xindy https://bugzilla.redhat.com/show_bug.cgi?id=1643664
latex_use_xindy = False

latex_domain_indices = False

latex_elements = {
    'makeindex': '',
    'printindex': '',
    'preamble': r'\setcounter{tocdepth}{3}',
}

# openstackdocstheme options
openstackdocs_repo_name = 'openstack/python-watcherclient'
openstackdocs_pdf_link = True
openstackdocs_bug_project = 'python-watcherclient'
openstackdocs_bug_tag = ''


#html_theme_options = {"show_other_versions": "True"}
