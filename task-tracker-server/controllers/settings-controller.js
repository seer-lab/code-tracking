// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const ERRORS = require('../consts/errors').ERRORS;
const LOGGER_NAME = require('../consts/consts').LOGGER_NAME;
const settingsService = require('../services/settings/settings-service');

const logger = intelLogger.getLogger(LOGGER_NAME);


const getSettings = async () => {
    const settings = await settingsService.getSettings();

    if (!settings) {
        logger.error(`${new Date()}: Settings are not exists`, new Error(`Settings are not exists`));
        return {
            error: ERRORS.VALIDATION.SETTINGS.NOT_EXISTS
        }
    }

    logger.info(`${new Date()}: Settings was received successfully`);
    return settings;
};

const createSettings = async (descriptions) => {
    const settings = await settingsService.getSettings();

    if (settings) {
        logger.error(`${new Date()}: Settings was not created`, new Error(`Settings are already taken`));
        return {
            error: ERRORS.VALIDATION.SETTINGS.ALREADY_TAKEN
        }
    }

    return await settingsService.createSettings(descriptions);
};

const deleteSettings = async () => {
    const settings = await settingsService.getSettings();

    if (!settings) {
        logger.error(`${new Date()}: Settings are not exists`, new Error(`Settings are not exists`));
        return {
            error: ERRORS.VALIDATION.SETTINGS.NOT_EXISTS
        }
    }

    logger.info(`${new Date()}: Settings was received successfully`);
    return await settingsService.deleteSettings(settings);
};

module.exports = {
    getSettings,
    createSettings,
    deleteSettings,
};
