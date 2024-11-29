// Copyright (c) 2020 Anastasiia Birillo

const LANGUAGES = require('../../consts/consts').LANGUAGES;
const dialogTextDescriptionDao = require('../../daos/dialog-text/dialog-text-description-dao');

const createDialogTextDescription = async (dialogTextDescription, language) => {
    if (LANGUAGES.indexOf(language) === -1) {
        return null;
    }
    return await dialogTextDescriptionDao.createDialogTextDescription(dialogTextDescription);
};

const deleteDialogTextDescription = async (dialogTextDescription) => {
    return await dialogTextDescriptionDao.deleteDialogTextDescription(dialogTextDescription);
};

module.exports = {
    createDialogTextDescription,
    deleteDialogTextDescription,
};
