from setuptools import setup

setup(
    name='camphor-schedule-notifier',
    version='1.0.0',
    description='CAMPHOR- Schedule Notifier',
    url='https://github.com/camphor-/schedule-notifier',
    author='CAMPHOR- (Yusuke Miyazaki)',
    author_email='support@camph.net',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    py_modules=['app'],
    install_requires=[
        'click>=6.0,<7.0',
        'kawasemi>=1.0.0,<2.0.0',
        'python-dateutil>=2.6.0,<3.0',
        'pytz>=2016.10',
    ],
    extras_require={
        "test": [
            "flake8>=3.4.0,<4.0.0",
            "mypy>=0.521,<1.0",
            "pytest>=3.2.0,<4.0.0",
            "tox>=2.5.0,<5.0.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'schedule-notifier=app:main',
        ],
    },
)
