const { step } = require('mocha-steps');
const assert = require('assert');
const { Chance } = require('chance');
const firefox = require('selenium-webdriver/firefox');
const { By, Builder, Key } = require('selenium-webdriver');
const { suite } = require('selenium-webdriver/testing');
require('geckodriver');

function verify_configuration(cfg) {
    for (const property in cfg) {
        if (typeof cfg[property] === 'undefined') {
            throw new Error('Property cfg.' + property + ' is undefined');
        } else if (typeof cfg[property] === 'string' && cfg[property].length === 0) {
            throw new Error('Property cfg.' + property + '" is empty');
        }
    }

    if (cfg.categories_names.length < 1) { throw new Error('cfg.categories_names requires atleast one category'); }
    if (cfg.products_per_category < 1) { throw new Error('cfg.products_per_category needs to be bigger than 0'); }
    if (cfg.min_quantity < 1) { throw new Error('cfg.min_quantity needs to be bigger than 0'); }
    if (cfg.max_quantity < cfg.min_quantity) { throw new Error('cfg.min_quantity needs to be bigger than cfg.max_quantity'); }
    if (cfg.products_to_remove >= cfg.categories_names.length * cfg.products_per_category) { throw new Error('cfg.products_to_remove cant be bigger than amount of products to add'); }
}

suite(function(env) {
    describe('Książker - Biznes Elektroniczny', function() {
        const chance = new Chance();
        const headless = process.env.HEADLESS;
        let driver;

        //---Test configuration---
        const cfg = {
            //--Product ordering--
            categories_names: ['Biografie', 'Fantastyka'], //category names to add products to cart from
            products_per_category: 5, //amount of products added to cart from each category
            min_quantity: 1, //minimum quantity of product to be randomized
            max_quantity: 10, //maximum quantity of product to be randomized
            products_to_remove: 1, //amount of products to remove from cart before making an order
            //--Registration--
            register_gender: '1', //1 - male, 2 - female
            register_firstname: chance.first({gender: 'male'}),
            register_lastname: chance.last(),
            register_email: chance.email({domain: 'prestatest.com'}), //doesnt need to be an actual email address, you can use your own email address to check if email actually gets sent
            register_password: 'test123_presta', //password needs to be strong enough
            //--Order information--
            order_address: 'Gabriela Narutowicza 11/12',
            order_postcode: '80-233',
            order_city: 'Gdańsk'
        };

        this.timeout(40000); //prevents tests from failing due to loading times

        before(async function() {
            verify_configuration(cfg);
            if (headless === 'true') {
                driver = await new Builder()
                .withCapabilities({"acceptInsecureCerts": true})
                .setFirefoxOptions(new firefox.Options().headless())
                .forBrowser('firefox')
                .build();
            } else {
                driver = await new Builder()
                .withCapabilities({"acceptInsecureCerts": true})
                .forBrowser('firefox')
                .build();
            }
        });

        after(async () => await driver.quit());

        step('Finding and adding products to cart', async function() {
            //load main page and navigate to 'Książki' category
            await driver.get('https://localhost:8002/');
            assert.equal(await driver.getTitle(), "Książker");

            await driver.manage().setTimeouts({ implicit: 500 });

            const category = await driver.findElement(By.className('dropdown-item'));
            assert.equal(await category.getText(), "KSIĄŻKI");
            let category_link = await category.getAttribute('href');
            
            //load 'Książki' category page
            await driver.get(category_link);
            assert.equal(await driver.getTitle(), "Książki");

            const submenu = await driver.findElements(By.css('.category-sub-menu a'));
            
            //find all categories
            let categories_links = {};
            for (let subcat of submenu) {
                let subcattext = await subcat.getText();

                for(let cat of cfg.categories_names) {
                    if (subcattext === cat) {
                        categories_links[cat] = await subcat.getAttribute('href');
                        break;
                    }
                }

                if (Object.keys(categories_links).length == cfg.categories_names.length) {
                    break;
                }
            }
            assert.equal(Object.keys(categories_links).length, cfg.categories_names.length);

            //for each category find product pages
            let product_links = [];
            for (let key in categories_links) {
                await driver.get(categories_links[key]);
                assert.equal(await driver.getTitle(), key);

                let products = await driver.findElements(By.css('#js-product-list .product'));
                products = await products.slice(0, cfg.products_per_category);

                for (let product of products) {
                    let link = await product.findElement(By.tagName('a'));
                    product_links.push(await link.getAttribute('href'));
                }
            }
            assert.equal(product_links.length, cfg.categories_names.length * cfg.products_per_category);

            //for each product page, add it to cart with random amount
            for (let product_link of product_links) {
                await driver.get(product_link);

                let amount = Math.floor(Math.random() * (cfg.max_quantity - 1)) + cfg.min_quantity;
                let quantity = await driver.findElement(By.id('quantity_wanted'));
                await quantity.sendKeys(Key.CONTROL + "a");
                await quantity.sendKeys(Key.DELETE);
                await quantity.sendKeys(amount.toString(), Key.ENTER);
                
                await driver.findElement(By.className('add-to-cart')).click();
            }
        });

        step('Verifying and removing products from cart', async function() {
            const cart = await driver.findElement(By.css('#_desktop_cart a'));
            await driver.get(await cart.getAttribute('href'));
            assert.equal(await driver.getTitle(), 'Koszyk');

            //check if all products were added
            let cart_items = await driver.findElements(By.className('cart-item'));
            assert.equal(cart_items.length, cfg.categories_names.length * cfg.products_per_category);

            //delete products
            let remove_links = await driver.findElements(By.className('remove-from-cart'));
            remove_links = remove_links.slice(0, cfg.products_to_remove);

            for (let remove_link of remove_links) {
                await remove_link.click();
            }

            //reload cart page
            driver.navigate().refresh();
            assert.equal(await driver.getTitle(), 'Koszyk');

            //check if product is actually deleted
            cart_items = await driver.findElements(By.className('cart-item'));
            assert.equal(cart_items.length, cfg.categories_names.length * cfg.products_per_category - cfg.products_to_remove);
        });

        step('Registering a new account', async function() {
            const login = await driver.findElement(By.css('#_desktop_user_info a'));
            await driver.get(await login.getAttribute('href'));

            const register = await driver.findElement(By.css('.no-account a'));
            await driver.get(await register.getAttribute('href'));

            await driver.findElement(By.id('field-id_gender-' + cfg.register_gender)).click();
            await driver.findElement(By.id('field-firstname')).sendKeys(cfg.register_firstname, Key.ENTER);
            await driver.findElement(By.id('field-lastname')).sendKeys(cfg.register_lastname, Key.ENTER);
            await driver.findElement(By.id('field-email')).sendKeys(cfg.register_email, Key.ENTER);
            await driver.findElement(By.id('field-password')).sendKeys(cfg.register_password, Key.ENTER);
            await driver.findElement(By.id('field-password')).sendKeys(cfg.register_password, Key.ENTER);
            await driver.findElement(By.name('customer_privacy')).click();

            await driver.findElement(By.className('form-control-submit')).click();

            const logout = await driver.findElement(By.css('#_desktop_user_info a'));
            assert(await logout.getText(), 'Wyloguj się');
        });

        step('Fillout order address form', async function() {
            const cart = await driver.findElement(By.css('#_desktop_cart a'));
            await driver.get(await cart.getAttribute('href'));
            assert.equal(await driver.getTitle(), 'Koszyk');

            const submit_order = await driver.findElement(By.css('.checkout a'));
            await driver.get(await submit_order.getAttribute('href'));

            //fillout address form
            await driver.findElement(By.id('field-address1')).sendKeys(cfg.order_address);
            await driver.findElement(By.id('field-postcode')).sendKeys(cfg.order_postcode);
            await driver.findElement(By.id('field-city')).sendKeys(cfg.order_city, Key.ENTER);
        });

        step('Choose delivery method', async function() {
            const deliveries = await driver.findElements(By.className('delivery-option'));
            for (let delivery of deliveries) {
                const delivery_name = await delivery.findElement(By.className('carrier-name'));
                if (await delivery_name.getText() === 'InPost - kurier') {
                    await delivery.findElement(By.tagName('input')).click();
                    break;
                }
            }

            await driver.findElement(By.name('confirmDeliveryOption')).click();
        });

        step('Choose payment method', async function() {
            const payments = await driver.findElements(By.className('payment-option'));
            for (let payment of payments) {
                const payment_name = await payment.findElement(By.tagName('label'));
                if (await payment_name.getText() === 'Zapłać gotówką przy odbiorze') {
                    await payment.findElement(By.tagName('input')).click();
                    break;
                }
            }

            await driver.findElement(By.id('conditions_to_approve[terms-and-conditions]')).click();

            await driver.findElement(By.css('#payment-confirmation button')).click();

            assert.equal(await driver.getTitle(), 'Potwierdzenie zamówienia');
        });

        step('Check order status', async function() {
            const footer = await driver.findElements(By.css('#footer_account_list a'));
            for (let link of footer) {
                if (await link.getText() === 'Zamówienia') {
                    await driver.get(await link.getAttribute('href'));
                    break;
                }
            }

            assert.equal(await driver.getTitle(), 'Historia zamówień');

            const details = await driver.findElement(By.className('view-order-details-link'));
            await driver.get(await details.getAttribute('href'));

            const order_history = await driver.findElement(By.id('order-history'));
            assert.equal(await order_history.findElement(By.tagName('h3')).getText(), 'SZCZEGÓŁY ZAMÓWIENIA');

            const status = await order_history.findElement(By.className('label'));
            assert.equal(await status.getText(), 'Oczekiwanie na płatność przy odbiorze');
        });
    });
});