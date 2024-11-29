// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const LANGUAGES = require('../../consts/consts').LANGUAGES;

const DialogTextSchema = new Schema({
    key: {type: String, unique: true},
    ru: { type: Schema.ObjectId, ref: 'DialogTextDescription' },
    en: { type: Schema.ObjectId, ref: 'DialogTextDescription' },
});

DialogTextSchema.methods.getPublicData = function () {
    return {};
};

DialogTextSchema.methods.getAsyncPublicData = async function () {
    let data = this.getPublicData();
    data['translation'] = [];
    for(const language of LANGUAGES){
        const currentLang = await this.populate(language).execPopulate();
        if (currentLang[language]) {
            data['translation'].push({
                'key': language
            });
            data['translation'].push(currentLang[language].getPublicData());
        }
    }
    return data;
};

module.exports = mongoose.model('DialogText', DialogTextSchema);
