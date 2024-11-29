// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const consts = require('../consts/consts');
const ERRORS = require('../consts/errors').ERRORS;
const BASE_URL = require('../consts/consts').BASE_URL;
const fileService = require('../services/file-service');
const dataItemController = require('../controllers/data-item-controller');

const logger = intelLogger.getLogger(consts.LOGGER_NAME);

module.exports = (app, upload) => {

    app.route(`${BASE_URL.DI}`).post(upload.single(consts.DI_UPLOADED_FILE), async (req, res, next) => {
            if (!req.file) {
                const error = ERRORS.VALIDATION.FILE.NOT_RECEIVED;
                logger.error(`${new Date()}: file was not received`, new Error('File was not received'));
                res.status(error.code);
                res.json(error.content);
                res.end();
            } else {
                const absolute_path = req.protocol + '://' + req.headers['host'] + '/' + req.file.path;
                let activityTrackerKey = -1;
                if (req.body && req.body.activityTrackerKey) {
                    activityTrackerKey = req.body.activityTrackerKey;
                }

                const response = await dataItemController.createDI(absolute_path, activityTrackerKey);
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

    app.route(`${BASE_URL.DI}/all`).get(async (req, res, next) => {
        const response = await dataItemController.getAllDi();
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.map(x => x.getPublicData()))
        }
    });

    app.route(`${BASE_URL.DI}/:id`).get(async (req, res, next) => {
        const response = await dataItemController.getDiByExternalId(req.params.id);
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData())
        }
    });
};
