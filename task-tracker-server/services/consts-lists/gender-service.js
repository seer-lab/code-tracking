// Copyright (c) 2020 Anastasiia Birillo

const LANGUAGES = require('../../consts/consts').LANGUAGES;
const genderDao = require('../../daos/consts-lists/gender-dao');

const createGender = async (key, descriptions) => {
    let preparedDescriptions = [];
    for(const description of descriptions){
        if (LANGUAGES.indexOf(description.language) > -1) {
            preparedDescriptions.push(description);
        }
    }
    return await genderDao.createGender(key, preparedDescriptions);
};

const getGenderByKey = async (key) => {
    return await genderDao.getGenderByKey(key);
};

const getAllGenders = async () => {
    return await genderDao.getAllGenders();
};

const deleteGender = async (gender) => {
    return await genderDao.deleteGender(gender);
};

module.exports = {
    createGender,
    deleteGender,
    getAllGenders,
    getGenderByKey,
};
