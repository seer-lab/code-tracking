// Copyright (c) 2020 Anastasiia Birillo

const BASE_URL = require('../../consts/consts').BASE_URL;
const genderController = require('../../controllers/consts-lists/gender-controller');

module.exports = (app) => {

    app.route(`${BASE_URL.GENDER}`).post(async (req, res, next) => {
        const response = await genderController.createGender(req.body.key.toLowerCase(), req.body.descriptions);
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData())
        }
    });

    app.route(`${BASE_URL.GENDER}/all`).get(async (req, res, next) => {
        const response = await genderController.getAllGenders();
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

    app.route(`${BASE_URL.GENDER}/:key`).get(async (req, res, next) => {
        const response = await genderController.getGenderByKey(req.params.key.toLowerCase());
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData())
        }
    });

    app.route(`${BASE_URL.GENDER}/:key`).delete(async (req, res, next) => {
        const response = await genderController.deleteGenderByKey(req.params.key.toLowerCase());
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData())
        }
    });

};
