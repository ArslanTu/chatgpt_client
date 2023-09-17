from setuptools import setup

setup(
    name='chatgpt_client',
    version='0.2.0',
    packages=['chatgpt_client'],
    install_requires=[
        # 添加你的依赖库（如果有的话）
        'openai==0.27.4',
        'tenacity'
    ],
    author='ArslanTu',
    author_email='arslantu@arslantu.xyz',
    description='Easily chat with ChatGPT.',
    url='https://github.com/arslantu/chatgpt_client',
)