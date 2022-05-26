brew bundle
pyenv virtualenv 3.9.11 yagro-project-env

source ~/.zshrc

cd ..
cd ygr-file-processing

pyenv exec pip install -r ./requirements.txt