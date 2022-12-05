# electronic_business - selenium-tests

Test made for *Firefox* browser only, to check if process of making an order is working properly. Made using *selenium-webdriver* and *mocha* test runner, written in *JavaScript*.

- [Installation](#contents)
    - [Requirements](#requirements)
    - [Installing dependencies](#installing-dependencies)
- [Running tests](#running-tests)
    - [Test configuration](#test-configuration)
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

To run test with browser UI enabled, type in console:

    npm run test

If you want to run test without browser UI (its faster and uses less resources):

    npm run headless_test

It will run script defined in **package.json**, test called *test* or *headless_test*, both defined in *scripts* section.

## Test configuration:

Test configuration is at the beginning of **order_test.spec.js** file:

    //---Test configuration---
    const cfg = {
        //--Product ordering--
        categories_names: ['Biografie', 'Fantastyka'],
        products_per_category: 5,
        min_quantity: 1,
        max_quantity: 10,
        products_to_remove: 1,
        //--Registration--
        register_gender: '1',
        register_firstname: chance.first({gender: 'male'}),
        register_lastname: chance.last(),
        register_email: chance.email({domain: 'prestatest.com'}),
        register_password: 'test123_presta',
        //--Order information--
        order_address: 'Gabriela Narutowicza 11/12',
        order_postcode: '80-233',
        order_city: 'Gdańsk'
    };

The configuration is verified before running tests. If there is anything wrong with the  provided configuration, mocha will return error with a message whats causing it.

Additional explanation of each property is in the actual file.

## Issues while running tests:

### Firefox issues

If Firefox throws exception: 

    Your Firefox profile cannot be loaded. It may be missing or inaccessible.

It means you have snap installation of Firefox. To reinstall Firefox as non-snap version follow this [tutorial](https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04).

### Mocha issues

If mocha throws exception:

    Error: Timeout of X ms exceeded. For async tests and hooks, ensure "done()" is called; if returning a Promise, ensure it resolves.

You need to change maximum timeouts for tests. Change this line to bigger value than current one:

    this.timeout(x);