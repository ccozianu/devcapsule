"""Playwright Python wheels and Chromium artifacts verified 2026-10-03.

Wheel hashes match PyPI; browser hashes computed from the version-specific
URLs shipped by Playwright 1.63.0. Ubuntu 24.04, CPython 3.12, x86-64 only.
"""

from typing import Any

PIN: dict[str, Any] = {'version': '1.63.0',
 'delivery-policy': 'local-materialization',
 'license': 'Apache-2.0',
 'platform': 'linux-amd64',
 'artifacts': {'greenlet': {'format': 'python-wheel',
                            'url': 'https://files.pythonhosted.org/packages/66/6a/1594f3869c57c149abdb380492529e04d4c0229b5e4d79572c5bd0aaa673/greenlet-3.5.6-cp312-cp312-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl',
                            'sha256': '975736b002ed080d124cf81a79cb7e05cb26d6b3f5c7a7b651c0fcce70353aa1',
                            'destination': '/opt/playwright'},
               'playwright': {'format': 'python-wheel',
                              'url': 'https://files.pythonhosted.org/packages/27/9c/103a5037789062bdab27c7dca53f3ca6b075b572ab2cd96eec825b3aec4e/playwright-1.63.0-py3-none-manylinux1_x86_64.whl',
                              'sha256': 'ad21bc07516b187965a7521c5cf0df0bd657b17482eaad74335272d35a2b07de',
                              'destination': '/opt/playwright'},
               'pyee': {'format': 'python-wheel',
                        'url': 'https://files.pythonhosted.org/packages/a0/c4/b4d4827c93ef43c01f599ef31453ccc1c132b353284fc6c87d535c233129/pyee-13.0.1-py3-none-any.whl',
                        'sha256': 'af2f8fede4171ef667dfded53f96e2ed0d6e6bd7ee3bb46437f77e3b57689228',
                        'destination': '/opt/playwright'},
               'typing_extensions': {'format': 'python-wheel',
                                     'url': 'https://files.pythonhosted.org/packages/49/d3/b8441a820a491ddfc024b0b0cf0393375b75ea13866d9c66727e54c2fc80/typing_extensions-4.16.0-py3-none-any.whl',
                                     'sha256': '481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8',
                                     'destination': '/opt/playwright'},
               'chromium-1243': {'format': 'zip-directory',
                                 'url': 'https://cdn.playwright.dev/builds/cft/153.0.8010.12/linux64/chrome-linux64.zip',
                                 'sha256': '8aac35011c18f6e2d10696154af89a5728ac2ddd6dc6fad24ffdf243c3fcfd5a',
                                 'destination': '/opt/playwright/browsers/chromium-1243'},
               'chromium_headless_shell-1243': {'format': 'zip-directory',
                                                'url': 'https://cdn.playwright.dev/builds/cft/153.0.8010.12/linux64/chrome-headless-shell-linux64.zip',
                                                'sha256': 'a9da028861a0cf789ff25c2fed45f5f1aaf969ed9247835b6a7821a4f7af9d1d',
                                                'destination': '/opt/playwright/browsers/chromium_headless_shell-1243'},
               'ffmpeg-1011': {'format': 'zip-directory',
                               'url': 'https://cdn.playwright.dev/dbazure/download/playwright/builds/ffmpeg/1011/ffmpeg-linux.zip',
                               'sha256': 'ebc74fc5b94830176a3c2914ae96bd8bc7f6a91f4f33890230f84a172ee61ccc',
                               'destination': '/opt/playwright/browsers/ffmpeg-1011'}}}
