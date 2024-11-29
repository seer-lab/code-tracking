// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const LANGUAGES = require('../../consts/consts').LANGUAGES;
const mongooseSequence = require('mongoose-sequence')(mongoose);

const TaskSchema = new Schema({
    key: {type: String, unique: true},
    ru: { type: Schema.ObjectId, ref: 'TaskDescription' },
    en: { type: Schema.ObjectId, ref: 'TaskDescription' },
    examples: [{
            input: {type: String},
            output: {type: String}
        }]
});

TaskSchema.plugin(mongooseSequence, {inc_field: 'externalTaskId'});

TaskSchema.methods.getPublicData = function () {
    return {
        key: this.key,
        examples: this.examples.map(function(example) {
            return {
                input: example.input,
                output: example.output
            }
        })
    };
};

TaskSchema.methods.getAsyncPublicData = async function () {
    let data = this.getPublicData();
    data['infoTranslation'] = [];
    for(const language of LANGUAGES){
        const currentLang = await this.populate(language).execPopulate();
        if (currentLang[language]) {
            data['infoTranslation'].push({
                'key': language
            });
            data['infoTranslation'].push(currentLang[language].getPublicData());
        }
    }
    return data;
};

module.exports = mongoose.model('Task', TaskSchema);
