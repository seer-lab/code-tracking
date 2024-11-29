// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const ERRORS = require('../consts/errors').ERRORS;
const LOGGER_NAME = require('../consts/consts').LOGGER_NAME;
const dialogTextService = require('../services/dialog-text/dialog-text-service');

const logger = intelLogger.getLogger(LOGGER_NAME);


const getDialogTextByKey = async (key) => {
    const dialogText = await dialogTextService.getDialogTextByKey(key);

    if (!dialogText) {
        logger.error(`${new Date()}: Dialog text ${key} is not exists`, new Error(`Dialog text ${key} is not exists`));
        return {
            error: ERRORS.VALIDATION.DIALOG_TEXT.NOT_EXISTS
        }
    }

    logger.info(`${new Date()}: Dialog text ${key} was received successfully`);
    return dialogText;
};

const createDialogText = async (key, descriptions) => {
    const dialogText = await dialogTextService.getDialogTextByKey(key);

    if (dialogText) {
        logger.error(`${new Date()}: Dialog text ${key} was not created`, new Error(`Dialog text ${key} is already taken`));
        return {
            error: ERRORS.VALIDATION.DIALOG_TEXT.ALREADY_TAKEN
        }
    }

    return await dialogTextService.createDialogText(key, descriptions);
};

const deleteDialogTextByKey = async (key) => {
    const dialogText = await dialogTextService.getDialogTextByKey(key);

    if (!dialogText) {
        logger.error(`${new Date()}: Dialog text ${key} is not exists`, new Error(`Dialog text ${key} is not exists`));
        return {
            error: ERRORS.VALIDATION.DIALOG_TEXT.NOT_EXISTS
        }
    }

    logger.info(`${new Date()}: Dialog text ${key} was deleted successfully`);
    return await dialogTextService.deleteDialogText(dialogText);
};

module.exports = {
    createDialogText,
    getDialogTextByKey,
    deleteDialogTextByKey
};
