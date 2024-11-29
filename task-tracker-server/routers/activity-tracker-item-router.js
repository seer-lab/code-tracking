// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const consts = require('../consts/consts');
const ERRORS = require('../consts/errors').ERRORS;
const BASE_URL = require('../consts/consts').BASE_URL;
const LOGGER_NAME = require('../consts/consts').LOGGER_NAME;
const atiController = require('../controllers/activity-tracker-item-controller');

const logger = intelLogger.getLogger(LOGGER_NAME);

module.exports = (app, upload) => {

    app.route(`${BASE_URL.ATI}`).post(upload.single(consts.ATI_UPLOADED_FILE), async (req, res, next) => {
        if (!req.file) {
            const error = ERRORS.VALIDATION.FILE.NOT_RECEIVED;
            logger.error(`${new Date()}: file was not received`, new Error('File was not received'));
            res.status(error.code);
            res.json(error.content);
            res.end();
        } else {
            const absolute_path = req.protocol + '://' + req.headers['host'] + '/' + req.file.path;
            const response = await atiController.createAti(absolute_path);
            if (response.error) {
                res.status(response.error.code);
                res.json(response.error.content);
                res.end();
            } else {
                res.json(response.getPublicData().id)
            }
        }
    });

    app.route(`${BASE_URL.ATI}/all`).get(async (req, res, next) => {
        const response = await atiController.getAllAti();
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.map(x => x.getPublicData()))
        }
    });

    app.route(`${BASE_URL.ATI}/:id`).get(async (req, res, next) => {
        const response = await atiController.getAtiByExternalId(req.params.id);
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData())
        }
    });
};
