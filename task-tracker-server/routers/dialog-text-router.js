// Copyright (c) 2020 Anastasiia Birillo

const BASE_URL = require('../consts/consts').BASE_URL;
const dialogTextController = require('../controllers/dialog-text-controller');

module.exports = (app, upload) => {

    app.route(`${BASE_URL.DIALOG_TEXT}`).post(async (req, res, next) => {
        const response = await dialogTextController.createDialogText(req.body.key.toLowerCase(), req.body.descriptions);
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(await response.getAsyncPublicData())
        }
    });

    app.route(`${BASE_URL.DIALOG_TEXT}/:key`).get(async (req, res, next) => {
        const response = await dialogTextController.getDialogTextByKey(req.params.key.toLowerCase());
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(await response.getAsyncPublicData())
        }
    });

    app.route(`${BASE_URL.TASK}/:key`).delete(async (req, res, next) => {
        const response = await dialogTextController.deleteDialogTextByKey(req.params.key.toLowerCase());
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(await response.getAsyncPublicData())
        }
    });

};
