const { Builder } = require('selenium-webdriver');
const { suite } = require('selenium-webdriver/testing');
const assert = require('assert');
require('geckodriver');

suite(function(env) {
    describe('Książker - Biznes Elektroniczny', function() {
        this.timeout(15000);
        let driver;

        before(async function() {
            driver = await new Builder().forBrowser('firefox').build();
        });

        after(async () => await driver.quit());

        it('Making an order', async function() {
            await driver.get('http://localhost:8001/');

            let title = await driver.getTitle();
            assert.equal("Książker", title);
        });

    });
});