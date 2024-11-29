// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const LANGUAGES = require('../../consts/consts').LANGUAGES;

const CountrySchema = new Schema({
    key: {type: String, unique: true},
    en: {type: String},
    ru: {type: String},
});


CountrySchema.methods.getPublicData = function () {
    const data = {
        key: this.key,
    };
    data['translation'] = [];
    for(const language of LANGUAGES){
        if (this[language]) {
            data['translation'].push({
                'key': language
            });
            data['translation'].push(this[language]);
        }
    }
    return data;
};

module.exports = mongoose.model('Country', CountrySchema);
