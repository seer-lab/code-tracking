// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const LANGUAGES = require('../../consts/consts').LANGUAGES;

const SettingsSchema = new Schema({
    en: { type: Schema.ObjectId, ref: 'SettingsDescription' },
    ru: { type: Schema.ObjectId, ref: 'SettingsDescription' },
});


SettingsSchema.methods.getPublicData = function () {
    return {};
};

SettingsSchema.methods.getAsyncPublicData = async function () {
    let data = this.getPublicData();
    const keys = ['surveyPane', 'taskChoosingPane', 'taskSolvingPane', 'finalPane', 'successPane'];
    keys.map(key => data[key] = []);
    for(const language of LANGUAGES){
        const currentLang = await this.populate(language).execPopulate();
        if (currentLang[language]) {
            const publicData = currentLang[language].getPublicData();
            keys.map(key => {
                data[key].push({
                    'key': language
                });
                data[key].push(publicData[key]);
            });
        }
    }
    return [data];
};

module.exports = mongoose.model('Settings', SettingsSchema);
