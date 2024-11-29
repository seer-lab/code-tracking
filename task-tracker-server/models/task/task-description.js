// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const TaskDescriptionSchema = new Schema({
    name: {type: String},
    description: {type: String},
    input: {type: String},
    output: {type: String},
});

TaskDescriptionSchema.methods.getPublicData = function () {
    return {
        name: this.name,
        description: this.description,
        input: this.input,
        output: this.output,
    };
};

module.exports = mongoose.model('TaskDescription', TaskDescriptionSchema);
