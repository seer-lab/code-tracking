// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');

const Gender = mongoose.model('Gender');

const formatterService = require('../../services/formatter-service');

const createGender = async (key, descriptions) => {
    const gender = new Gender({
        key: key
    });
    for(const description of descriptions){
        gender[description.language] = formatterService.toLowerCase(description.value);
    }
    return await gender.save();
};

const getGenderByKey = async (key) => {
    return await Gender.findOne({
        key: key
    })
};

const getAllGenders = async () => {
    return await Gender.find();
};

const deleteGender = async (gender) => {
    return await gender.remove();
};

module.exports = {
    createGender,
    deleteGender,
    getAllGenders,
    getGenderByKey,
};
