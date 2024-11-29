// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const consts = require('../consts/consts');
const BASE_URL = require('../consts/consts').BASE_URL;

const logger = intelLogger.getLogger(consts.LOGGER_NAME);

module.exports = (app) => {

    app.route(`${BASE_URL.LANGUAGE}/all`).get( (req, res, next) => {
        logger.info(`${new Date()}: ${consts.LANGUAGES.length} languages were received successfully`);
        res.json(consts.LANGUAGES.map(lang => { return { 'key': lang} }));
    });

};
