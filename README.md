# Website backend for a new claytontv

This is a django based webapp that will scrape videos and their metadata from curated christian media sites, providing a searchable interface as well as an alternative platform for viewing sunday service livestreams.

## About

NB: beginning by following this tutorial to throw together a starting point:
https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website



### Project Team


## Built With

This section is intended to list the frameworks and tools you're using to develop this software. Please link to the home page or documentation in each case.

Thinking Django backend and need to decide on frontend. Angular, React, tailwind?? https://medium.com/@StartXLabs/choosing-the-best-front-end-framework-for-django-5beb7a89cf87 

[Framework 1](https://something.com)  
[Framework 2](https://something.com)  
[Framework 3](https://something.com)  

## Getting Started

### Prerequisites

Any tools or versions of languages needed to run code. For example, specific Python or Node versions. Minimum hardware requirements also go here.

### Installation

How to build or install the application.

### Running Locally

How to run the application on your local system.

NB:
`python3 manage.py makemigrations`
`python3 manage.py migrate`

Need to run these commands every time your models change in a way that will affect the structure of the data that needs to be stored (including both addition and removal of whole models and individual fields).


### Running Tests

How to run tests on your local system.

## Deployment

### Local

Deploying to a production-style setup but on the local system. 
Todo this:
- cd into the ClaytonWeb folder
- make sure you are working in the correct virtual environment (`workon claytontv_env`)
- run `python3 manage.py runserver`

This should launch the site to your localhost ip and give you this ip address in the console output. Click the address to launch a webpage displaying the site.

### Production

Current demo deployment on fhing.pythonanywhere.com

To update following a new pull request to main:
- Open a bash terminal using the console link on the main page
- make sure you are in the correct environment `workon locallibraryenv`
- cd into the fhings.pythonanywhere.com folder
- pull changes from github with `git pull`
- fix any conflicts and commit
- switch to the web view (burger menu to the top right)
- Reload the site
- test changes clicking the url link to launch in browser
- Make sure to push any changes back to main if a merge was required.


## Usage

Any links to the production environment, video demos and screenshots.

## Roadmap

- [x] Initial Research  
- [ ] Minimum viable product <-- You are Here  
- [ ] Alpha Release  
- [ ] Feature-Complete Release  

## Contributing

### Main Branch
Protected and can only be pushed to via pull requests. It should be considered stable and a representation of production code.

### Dev Branch
Should be considered fragile; code should compile and run, but features may be prone to errors.

### Feature Branches
A branch per feature that is being worked on.

https://nvie.com/posts/a-successful-git-branching-model/

Check your current branch by typing `git branch` in the terminal (canopen one in vs code from the top menu bar).

To switch branch type `git checkout branchname` where branchname is the branch you want.

## License


## Acknowledgements
