// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const dialogTextDao = require('../../daos/dialog-text/dialog-text-dao');
const LOGGER_NAME = require('../../consts/consts').LOGGER_NAME;
const dialogTextDescriptionService = require('./dialog-text-description-service');

const logger = intelLogger.getLogger(LOGGER_NAME);

const createDialogText = async (key, descriptions) => {
    let preparedDescriptions = [];
    for(const description of descriptions){
        const dt = await dialogTextDescriptionService.createDialogTextDescription(description.info, description.language);
        if (dt) {
            preparedDescriptions.push({
                language: description.language,
                dt: dt
            });
        }
    }
    try {
        const dialogText = await dialogTextDao.createDialogText(key, preparedDescriptions);
        logger.info(`${new Date()}: Dialog text ${key} was created successfully`);
        return dialogText;
    } catch (e) {
        logger.error(`${new Date()}: Dialog text ${key} was not created`, e);
        for(const dt of preparedDescriptions){
            await dialogTextDescriptionService.deleteDialogTextDescription(dt);
        }
        return {
            error: ERRORS.INTERNAL_SERVER
        };
    }
};

const getDialogTextByKey = async (key) => {
    return await dialogTextDao.getDialogTextByKey(key);
};

const deleteDialogText = async (dialogText) => {
    return await dialogTextDao.deleteDialogText(dialogText);
};

module.exports = {
    createDialogText,
    getDialogTextByKey,
    deleteDialogText
};
