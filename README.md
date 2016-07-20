
# Betterlife Intelligent PSI

Flask based Intelligent PSI(Purchase, Sales and Inventory) management system

----
[![Travis Build Status](https://img.shields.io/travis/betterlife/psi.svg?label=Travis)](https://travis-ci.org/betterlife/psi)
[![Code Coverage](https://img.shields.io/codecov/c/github/betterlife/psi.svg?label=Coverage)](http://codecov.io/github/betterlife/psi?branch=master)
[![Code Climate](https://img.shields.io/codeclimate/github/betterlife/psi.svg?label=Grade)]()
[![Code Health](https://landscape.io/github/betterlife/psi/master/landscape.svg?style=flat)](https://landscape.io/github/betterlife/psi/master)
[![Requirements Status](https://requires.io/github/betterlife/psi/requirements.svg?branch=master)](https://requires.io/github/betterlife/psi/requirements/?branch=master)

[![license](https://img.shields.io/github/license/betterlife/psi.svg)](http://doge.mit-license.org)
[![Release](https://img.shields.io/github/release/betterlife/psi.svg)](http://github.com/betterlife/psi/releases)
[![All Downloads](https://img.shields.io/github/downloads/betterlife/psi/total.svg?label=Downlaods)](http://github.com/betterlife/psi/releases)
[![commits since release](https://img.shields.io/github/commits-since/betterlife/psi/V0.6.4.svg)](http://github.com/betterlife/psi/releases)

Try to answer follow questions:

  - Which product generates the most revenue/profit in my store and what's the data?
  - When do I need to replenish the stock and how much do I lost if that's not done?
  - What is the optimized quantity/date for replenish the stock?
  
Install & Deploy
  -  [Installation Locally](https://github.com/betterlife/psi/wiki/Installation)
  -  [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
  
How to run?

  - Start the application

    - Be sure to startup postgresql, then set up the follow environment variables firstly:

        - Required environment variables
          - DATABASE_URL
          - SECRET_KEY
          - SECURITY_PASSWORD_SALT
        - Necessary for some feature
          - SENTRY_DSN if want sentry to be enable
          - CLOUDINARY_URL if want cloudinary to be enable

    - For development, run **python wsgi.py**, and then open it on __[http://localhost:5000](http://localhost:5000)__
    - If you run it via **heroku local**, please open it on __[http://localhost:8000](http://localhost:8000)__
  - Test the application
    - Run **./scripts/run_tests.py** to test the application
  - Default admin username/password is __support<i></i>@betterlife.io / password__

Links:

  - [Dev environment](https://psi-dev.herokuapp.com/)
    - Organization user: __support@betterlife.io / password__
    - Business user: __business@betterlife.io / password__

Code Coverage History

![codecov.io](http://codecov.io/github/betterlife/psi/branch.svg?branch=master)
    
Betterlife PSI uses [MIT License](https://github.com/betterlife/flask-psi/blob/master/LICENSE)
