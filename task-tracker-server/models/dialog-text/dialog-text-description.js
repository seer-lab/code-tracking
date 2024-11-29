// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const DialogTextDescriptionSchema = new Schema({
    header: {type: String},
    description: {type: String},
});

DialogTextDescriptionSchema.methods.getPublicData = function () {
    return {
        header: this.header,
        description: this.description
    };
};

module.exports = mongoose.model('DialogTextDescription', DialogTextDescriptionSchema);
