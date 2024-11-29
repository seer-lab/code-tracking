// Copyright (c) 2020 Anastasiia Birillo

const LANGUAGES = require('../../consts/consts').LANGUAGES;
const settingsDescriptionDao = require('../../daos/settings/settings-description-dao');

const createSettingsDescription = async (settingsDescription, language) => {
    if (LANGUAGES.indexOf(language) === -1) {
        return null;
    }
    return await settingsDescriptionDao.createSettingsDescription(settingsDescription);
};

const deleteSettingsDescription = async (settingsDescription) => {
    return await settingsDescriptionDao.deleteSettingsDescription(settingsDescription);
};

module.exports = {
    createSettingsDescription,
    deleteSettingsDescription,
};
