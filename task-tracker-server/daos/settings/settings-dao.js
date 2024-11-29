// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');

const Settings = mongoose.model('Settings');
const LANGUAGES = require('../../consts/consts').LANGUAGES;
const settingsDescriptionDao = require('./settings-description-dao');

const createSettings = async (descriptions) => {
    const settings = new Settings({});
    for(const description of descriptions){
        settings[description.language] = description.sd._id;
    }
    return await settings.save();
};

const getSettings = async () => {
    const settings = await Settings.find();
    if (settings.length === 1) {
        return settings[0];
    }
    return null;
};

const deleteSettings = async (settings) => {
    for(const language of LANGUAGES){
        const description = await settings.populate(language).execPopulate();
        await settingsDescriptionDao.deleteSettingsDescription(description[language]);
    }
    return await settings.remove();
};

module.exports = {
    getSettings,
    deleteSettings,
    createSettings,
};
