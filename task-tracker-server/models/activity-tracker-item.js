// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const mongooseSequence = require('mongoose-sequence')(mongoose);

const AtiSchema = new Schema({
    codePath: {type: String},
    createdAt: { type: Date, default: Date.now }
});

AtiSchema.plugin(mongooseSequence, {inc_field: 'externalAtiId'});

AtiSchema.methods.getPublicData = function () {
    return {
        codePath: this.codePath,
        id: this.externalAtiId,
        createdAt: this.createdAt
    };
};

module.exports = mongoose.model('ActivityTrackerItem', AtiSchema);
