// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const consts = require('../consts/consts');
const ERRORS = require('../consts/errors').ERRORS;
const BASE_URL = require('../consts/consts').BASE_URL;
const fileService = require('../services/file-service');
const hintItemController = require('../controllers/hint-item-controller');

const logger = intelLogger.getLogger(consts.LOGGER_NAME);

module.exports = (app, upload) => {

    app.route(`${BASE_URL.HINT_ITEM}`).post(upload.single(consts.HINT_ITEM_UPLOADED_FILE), async (req, res, next) => {
            if (!req.file) {
                const error = ERRORS.VALIDATION.FILE.NOT_RECEIVED;
                logger.error(`${new Date()}: file was not received`, new Error('File was not received'));
                res.status(error.code);
                res.json(error.content);
                res.end();
            } else {
                const absolute_path = req.protocol + '://' + req.headers['host'] + '/' + req.file.path;
                const response = await hintItemController.createHintItem(absolute_path);
                if (response.error) {
                    await fileService.deleteFile(req.file.path);
                    res.status(response.error.code);
                    res.json(response.error.content);
                    res.end();
                } else {
                    res.json(response.getPublicData().id)
                }
            }
        }
    );

    app.route(`${BASE_URL.HINT_ITEM}/all`).get(async (req, res, next) => {
        const response = await hintItemController.getAllHintItems();
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.map(x => x.getPublicData()))
        }
    });

    app.route(`${BASE_URL.HINT_ITEM}/:id`).get(async (req, res, next) => {
        const response = await hintItemController.getHintItemByExternalId(req.params.id);
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData())
        }
    });
};
