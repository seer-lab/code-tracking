// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');

const Country = mongoose.model('Country');

const createCountry = async (key, descriptions) => {
    const country = new Country({
        key: key
    });
    for(const description of descriptions){
        country[description.language] = description.value;
    }
    return await country.save();
};

const getCountryByKey = async (key) => {
    return await Country.findOne({
        key: key
    })
};

const getAllCountries = async () => {
    return await Country.find();
};

const deleteCountry = async (country) => {
    return await country.remove();
};

module.exports = {
    createCountry,
    deleteCountry,
    getAllCountries,
    getCountryByKey,
};
