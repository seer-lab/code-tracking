// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');

const DialogText = mongoose.model('DialogText');
const LANGUAGES = require('../../consts/consts').LANGUAGES;
const dialogTextDescriptionDao = require('./dialog-text-description-dao');

const createDialogText = async (key, descriptions) => {
    const dt = new DialogText({
        key: key
    });
    for(const description of descriptions){
        dt[description.language] = description.dt._id;
    }
    return await dt.save();
};

const getDialogTextByKey = async (key) => {
    return await DialogText.findOne({
        key: key
    })
};

const deleteDialogText = async (dialogText) => {
    for(const language of LANGUAGES){
        const description = await dialogText.populate(language).execPopulate();
        await dialogTextDescriptionDao.deleteDialogTextDescription(description[language]);
    }
    return await dialogText.remove();
};

module.exports = {
    createDialogText,
    getDialogTextByKey,
    deleteDialogText
};
