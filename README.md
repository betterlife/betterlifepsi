
# Betterlife Intelligent PSI  [![Travis (.org)](https://img.shields.io/travis/com/betterlife/betterlifepsi.svg?logo=travis&style=flat-square)](https://travis-ci.com/betterlife/betterlifepsi) [![Code Coverage](https://img.shields.io/codecov/c/github/betterlife/betterlifepsi.svg?label=Coverage&style=flat-square)](http://codecov.io/github/betterlife/betterlifepsi?branch=master)

Intelligent PSI(Purchase, Sales and Inventory) management system

![GitHub](https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square)
[![Code Health](https://landscape.io/github/betterlife/betterlifepsi/master/landscape.svg?style=flat-square)](https://landscape.io/github/betterlife/betterlifepsi/master)
[![Requires.io](https://img.shields.io/requires/github/betterlife/betterlifepsi.svg?style=flat-square)](https://requires.io/github/betterlife/betterlifepsi/requirements/?branch=master)
[![commits since release](https://img.shields.io/github/commits-since/betterlife/betterlifepsi/V0.6.8.svg?style=flat-square)](http://github.com/betterlife/betterlifepsi/releases)
[![Release](https://img.shields.io/github/release/betterlife/betterlifepsi.svg?style=flat-square)](http://github.com/betterlife/betterlifepsi/releases) 
[![PyPI](https://img.shields.io/pypi/v/betterlifepsi.svg?style=flat-square)](https://pypi.org/project/betterlifepsi/)


## Try to answer some questions like

  - Which product generates the most revenue/profit in my store and what's the data?
  - When do I need to replenish the stock and how much do I lost if that's not done?
  - What is the optimized quantity/date for replenish the stock?
  
## Install & Run & Deploy  

  - Run using Docker (Recommend)

    * Make sure docker is installed and configured correctly. 
    * Clone the code via `git clone https://github.com/betterlife/betterlifepsi.git`
    * `cd betterlifepsi && docker-compose build && docker-compose up` to build and run the docker image
    * Please notice the database data is mounted to a docker volume called psi_data by default.

  - Install and run locally
    * Clone the code via `git clone https://github.com/betterlife/betterlifepsi.git`
    * `pip install -r requirements.txt` to install runtime dependencies.
    * `pip install -r etc/requirements/test.txt` to install development dependencies.
    * Create postgresql database and user for the application.
    * Set follow environment variables:
      * DATABASE_URL : Database URL, only postgresql is tested as of now.
      * FLASK_APP: Should be set to `psi.cli:application`
      * SECURITY_PASSWORD_SALT : password salt for password generation
      * SECRET_KEY : secret key for password generation
      * CLOUDINARY_URL : Cloudinary URL if use cloudinary to store image attachments
      * SENTRY_DSN : Sentry DSN if use sentry to handle exceptions 
    * `flask run` to run the application
    * Set environment variable `TEST_DATABASE_URL` and invoke `flask test` to run tests.

  - Install and run on heroku
    * Click button [![Deploy](https://img.shields.io/badge/Heroku-Deploy-brightgreen.svg?style=flat-square)](https://heroku.com/deploy)  to deploy current version to heroku.

## Links

  - [Demo environment](https://psi-dev.herokuapp.com/)
    - Organization administrator user: super_admin / password
    - Business user: bu / password
  - [Knowledge Center](https://github.com/betterlife/psi/wiki)    
  - [Story management](https://betterlife.atlassian.net)

## License    
Betterlife PSI uses [MIT License](https://github.com/betterlife/flask-psi/blob/master/LICENSE)
