// Copyright (c) 2020 Anastasiia Birillo

const BASE_URL = require('../consts/consts').BASE_URL;
const settingsController = require('../controllers/settings-controller');

module.exports = (app) => {

    app.route(`${BASE_URL.SETTINGS}`).post(async (req, res, next) => {
        const response = await settingsController.createSettings(req.body.descriptions);
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(await response.getAsyncPublicData())
        }
    });

    app.route(`${BASE_URL.SETTINGS}`).get(async (req, res, next) => {
        const response = await settingsController.getSettings();
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(await response.getAsyncPublicData())
        }
    });

    app.route(`${BASE_URL.SETTINGS}`).delete(async (req, res, next) => {
        const response = await settingsController.deleteSettings();
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(await response.getAsyncPublicData())
        }
    });

};
