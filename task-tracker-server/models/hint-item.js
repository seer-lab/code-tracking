// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const mongooseSequence = require('mongoose-sequence')(mongoose);

const HintItemSchema = new Schema({
    codePath: { type: String },
    createdAt: { type: Date, default: Date.now }
});

HintItemSchema.plugin(mongooseSequence, {inc_field: 'externalHintItemId'});

HintItemSchema.methods.getPublicData = function () {
    return {
        codePath: this.codePath,
        id: this.externalHintItemId
    };
};

module.exports = mongoose.model('HintItem', HintItemSchema);
