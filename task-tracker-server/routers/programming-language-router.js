// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const consts = require('../consts/consts');
const BASE_URL = require('../consts/consts').BASE_URL;

const logger = intelLogger.getLogger(consts.LOGGER_NAME);

module.exports = (app) => {

    app.route(`${BASE_URL.PROGRAMMING_LANGUAGE}/all`).get((req, res, next) => {
        logger.info(`${new Date()}: ${consts.PROGRAMMING_LANGUAGES.length} programming languages were received successfully`);
        res.json(consts.PROGRAMMING_LANGUAGES.map(lang => { return { 'key': lang} }));
    });

};
