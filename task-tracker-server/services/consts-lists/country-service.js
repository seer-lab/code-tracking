// Copyright (c) 2020 Anastasiia Birillo

const LANGUAGES = require('../../consts/consts').LANGUAGES;
const countryDao = require('../../daos/consts-lists/country-dao');

const createCountry = async (key, descriptions) => {
    let preparedDescriptions = [];
    for(const description of descriptions){
        if (LANGUAGES.indexOf(description.language) > -1) {
            preparedDescriptions.push(description);
        }
    }
    return await countryDao.createCountry(key, preparedDescriptions);
};

const getCountryByKey = async (key) => {
    return await countryDao.getCountryByKey(key);
};

const getAllCountries = async () => {
    return await countryDao.getAllCountries();
};

const deleteCountry = async (country) => {
    return await countryDao.deleteCountry(country);
};

module.exports = {
    createCountry,
    deleteCountry,
    getAllCountries,
    getCountryByKey,
};
