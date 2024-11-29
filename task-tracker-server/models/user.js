// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const mongooseSequence = require('mongoose-sequence')(mongoose);

const UserSchema = new Schema({
    data: [
        {
            activityTrackerKey: {type: String},
            dataItemKey: {type: String},
        }
    ]
});

UserSchema.plugin(mongooseSequence, {inc_field: 'externalStudentId'});

UserSchema.methods.getPublicData = function () {
    let res = {
        id: this.externalStudentId,
        data: []
    };
    for(const item of this.data) {
        res.data.push({
            atiId: item.activityTrackerKey,
            diId: item.dataItemKey
        })
    }
    return res;
};

module.exports = mongoose.model('User', UserSchema);
