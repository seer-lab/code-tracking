// Copyright (c) 2020 Anastasiia Birillo

const BASE_URL = require('../../consts/consts').BASE_URL;
const countryController = require('../../controllers/consts-lists/country-controller');

module.exports = (app) => {

    app.route(`${BASE_URL.COUNTRY}`).post(async (req, res, next) => {
        const response = await countryController.createCountry(req.body.key.toLowerCase(), req.body.descriptions);
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData())
        }
    });

    app.route(`${BASE_URL.COUNTRY}/all`).get(async (req, res, next) => {
        const response = await countryController.getAllCountries();
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.map(function (gender) {
                return gender.getPublicData();
            }));
        }
    });

    app.route(`${BASE_URL.COUNTRY}/:key`).get(async (req, res, next) => {
        const response = await countryController.getCountryByKey(req.params.key.toLowerCase());
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData())
        }
    });

    app.route(`${BASE_URL.COUNTRY}/:key`).delete(async (req, res, next) => {
        const response = await countryController.deleteCountryByKey(req.params.key.toLowerCase());
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData())
        }
    });

};
