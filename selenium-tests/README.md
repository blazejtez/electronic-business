# electronic_business - selenium-tests

Test made for *Firefox* browser only, to check if process of making an order is working properly. Made using *selenium-webdriver* and *mocha* test runner, written in *JavaScript*.

- [Installation](#contents)
    - [Requirements](#requirements)
    - [Installing dependencies](#installing-dependencies)
- [Running tests](#running-tests)
    - [Issues while running tests](#issues-while-running-tests)
        - [Firefox issues](#firefox-issues)
        - [Mocha issues](#mocha-issues)

# Installation

## Requirements:

|package|version|
|-------|-------|
|Node.js|>= 14.20.0|
|npm|>= 8.0.0|
|firefox|non-snap installation|

## Installing dependencies:

From **selenium-tests** directory, run:

    npm install

It will create **node_modules** containing all required dependencies to run Selenium tests.

# Running tests

To run tests, type in console:

    npm run test

It will run script defined in **package.json**, test called *test* defined in *scripts* section.

## Issues while running tests:

### Firefox issues

If Firefox throws exception: 

    Your Firefox profile cannot be loaded. It may be missing or inaccessible.

It means you have snap installation of Firefox. To reinstall Firefox as non-snap version follow this [tutorial](https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04).

### Mocha issues

If mocha throws exception:

    Error: Timeout of X ms exceeded. For async tests and hooks, ensure "done()" is called; if returning a Promise, ensure it resolves.

You need to change maximum timeouts for tests. Change these lines to higher values:

    this.timeout(x);