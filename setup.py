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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    py_modules=['app'],
    install_requires=[
        'click>=6.0,<7.0',
        'django-channels>=0.4.0,<0.5.0',
        'python-dateutil>=2.6.0,<3.0'
    ],
    entry_points={
        'console_scripts': [
            'schedule-notifier=app:main',
        ],
    },
)
