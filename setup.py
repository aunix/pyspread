#!/usr/bin/env python

from distutils.core import setup
from distutils.sysconfig import get_python_lib

setup(name='pyspread',
      version='0.1.3',
      description='A spreadsheet that accepts python expressions in its cells.',
      license='GPL v3 :: GNU General Public License',
      classifiers=[ 'Development Status :: 4 - Beta',
                    'Environment :: X11 Applications :: GTK',
                    'Intended Audience :: End Users/Desktop',
                    'License :: OSI Approved :: GNU General Public License (GPL)',
                    'Natural Language :: English',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python :: 2.5',
                    'Programming Language :: Python :: 2.6',
                    'Topic :: Office/Business :: Financial :: Spreadsheet',
      ],
      author='Martin Manns',
      author_email='mmanns@gmx.net',
      url='http://pyspread.sourceforge.net',
      install_requires=['numpy (>=1.1)', 'wx (>=2.8.10)'],
      scripts=['src/pyspread.py', 'src/pyspread'],
      packages=['_pyspread'],
      package_data={'_pyspread': 
                    ['share/icons/*.png', 'share/icons/actions/*.png', 
                     'share/icons/toggles/*.png', 'share/icons/toggles/*.xpm',
                     'examples/*', 'doc/help/*.html', 
                     'doc/help/images/*.png', 'README', 'COPYING']},
)
