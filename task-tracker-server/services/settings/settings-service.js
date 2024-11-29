// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const settingsDao = require('../../daos/settings/settings-dao');
const LOGGER_NAME = require('../../consts/consts').LOGGER_NAME;
const settingsDescriptionService = require('./settings-description-service');

const logger = intelLogger.getLogger(LOGGER_NAME);

const createSettings = async (descriptions) => {
    let preparedDescriptions = [];
    for(const description of descriptions){
        const sd = await settingsDescriptionService.createSettingsDescription(description.info, description.language);
        if (sd) {
            preparedDescriptions.push({
                language: description.language,
                sd: sd
            });
        }
    }
    try {
        const settings = await settingsDao.createSettings(preparedDescriptions);
        logger.info(`${new Date()}:Settings was created successfully`);
        return settings;
    } catch (e) {
        logger.error(`${new Date()}: Settings was not created`, e);
        for(const sd of preparedDescriptions){
            await settingsDescriptionService.deleteSettingsDescription(sd);
        }
        return {
            error: ERRORS.INTERNAL_SERVER
        };
    }
};

const getSettings = async () => {
    return await settingsDao.getSettings();

};

const deleteSettings = async (settings) => {
    return await settingsDao.deleteSettings(settings);
};

module.exports = {
    getSettings,
    createSettings,
    deleteSettings,
};
