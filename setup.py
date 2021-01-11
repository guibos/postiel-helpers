from distutils.core import setup
setup(
  name='postiel_helpers',
  packages=['postiel_helpers'],
  version='0.1',
  license='Mozilla Public License Version 2.0',
  description='Postiel helpers',
  author='guibos',
  url='https://github.com/guibos/postiel-helpers',
  download_url='https://github.com/guibos/postiel-helpers/archive/0.1.tar.gz',
  keywords=['postiel', 'helpers', 'value objects'],
  install_requires=[line.strip() for line in open("requirements.txt", "r").readlines()],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: Mozilla Public License Version 2.0',
    'Programming Language :: Python :: 3.8',
  ],
)
