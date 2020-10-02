from distutils.core import setup
setup(
  name='postiel_helpers',         # How you named your package folder (MyLib)
  packages=['postiel_helpers'],   # Chose the same as "name"
  version='0.1',      # Start with a small number and increase it with every change you make
  license='Mozilla Public License Version 2.0',
  description='Postiel helpers',   # Give a short description about your library
  author='guibos',                   # Type in your name
  # author_email='your.email@domain.com',      # Type in your E-Mail
  url='https://github.com/guibos/postiel-helpers',   # Provide either the link to your github or to your website
  download_url='https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords=['postie', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'dataclasses-json',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: Mozilla Public License Version 2.0',   # Again, pick a license
    'Programming Language :: Python :: 3.8',
  ],
)
