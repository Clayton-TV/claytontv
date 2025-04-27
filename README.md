# The official website for Clayton TV

<img width="1672" alt="image" src="https://github.com/Clayton-TV/claytontv/assets/14878653/c2c09122-1118-4b3c-bfbb-3d3b9516915d">

\*This is a demo site, soon to undergo substantial changes! Join our hackathon!

## Getting Started

To get started, you'll need to install a few things. All the tech used is cross-platform, but there will still be a few differences for macOS, Windows and Linux users.

Please follow the instructions carefully, and raise an issue for anything that doesn't work!

### Prerequisites

One of the following code editors (aka an Integrated Development Environment, or IDE)
- [VS Code](https://code.visualstudio.com/) (Free! You'll likely want the [Django extension](https://marketplace.visualstudio.com/items?itemName=batisteo.vscode-django) too)
- [PyCharm](https://www.jetbrains.com/toolbox-app/) (Pycharm Community is free, Pycharm Pro is Paid/Trial. Or, download the toolbox and install the Release Candidate, which is free but not always stable.)
- If you dare, you can use Atom, Sublime, or (please don't) Notepad++.

GitHub Desktop (A nice UI for git, the version management software. It will install git for you if you don't already have it.)
- https://desktop.github.com/ (Mac and Windows only. Linux users, you're likely familiar with terminal commands anyway, but check out [Oh-My-Zsh](https://github.com/ohmyzsh/ohmyzsh?tab=readme-ov-file#basic-installation) and their [git plugin](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/git))

Python (the programming language that our Django app uses)
- [Python 3.13.1](https://www.python.org/downloads/release/python-3131/) (Select the `Windows installer (64-bit)` or `macOS 64-bit universal2 installer`, depending on your OS. Linux users you can follow [this guide](https://ubuntuhandbook.org/index.php/2024/02/install-python-3-13-ubuntu/))
- Note: for users that use an existing Python version, don't worry, you can have multiple versions installed at a time. We'll use `pipenv` to auto-configure the app to use 3.13.

> Note: If you have Python 3.12 or earlier, you may need to install [Python 3.13](https://www.python.org/downloads/release/python-3131/). You can do this by running the following command in your terminal:
> ```sh
> pipenv --python 3.13
> ```

Node.js (for the front-end design of our app)
- [Node 20.12.2 LTS](https://nodejs.org/en/download) (Long-Term Support, or LTS, means that it will get features and security updates for longer)
- Alternatively, for Mac or Linux users, check out [Node Version Manager](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating). This requires technical skill to set up.

### Install instructions

Clone the repo in Github Desktop, or run the following command in a terminal window (`Note:` you may need to use a Command Prompt on Windows, as a git shell or PowerShell may not work).
```sh
git clone git@github.com:Clayton-TV/claytontv
```

Open the project in your editor, or change directory into the project
```sh
cd claytontv
```

Set up python environment
```sh
# Install pipenv
python3.13 -m pip install pipenv

#Above command may fail in MacOS (x86_64 Intel chip) - instead this works, then continue as before.
brew install pipenv

# Start pipenv
pipenv shell
```

Install python dependencies
```sh
pipenv install
```

Install the node dependencies
```sh
npm install
```

Run the migrations
```sh
python manage.py migrate
```

Launch the app
```sh
# Run the python server (backend)
python manage.py runserver
```
Open a new terminal window, using the virtual environment as before, and run:
```sh
# Run the vite server (frontend)
npm run dev
```
Go to [http://localhost:8000](http://localhost:8000) and you should see the image at the top of this README file.

### Troubleshooting

1. npm install error - Check you're in the right place - "cd" or do from VSCode
2. python not found - check environment variables - add python to the path and restart
3. commands need "pipenv run" prefix

### Useful Tips
- On Windows you can open cmd at a specific folder by navigating there and typing CMD in the location bar of the explorer window.
   
## Contributing

To report a bug, please [raise an issue](https://github.com/Clayton-TV/claytontv/issues/new). Include steps to replicate and a screenshot of the error.

To suggest a feature, please [raise an issue](https://github.com/Clayton-TV/claytontv/issues/new). Add a brief summary of the changes and any additional details.

To commit changes, please create a branch in the pattern of `bug/title-of-bug` or `feature/title-of-feature`. 

## Licence
