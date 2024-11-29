// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require("mongoose");
const DI = mongoose.model("DataItem");

const createDI = async (codePath, activityTrackerKey) => {
    const di = new DI({
        codePath: codePath,
        activityTrackerKey: activityTrackerKey
    });
    return await di.save();
};

const getDiByExternalId = async (externalId) => {
    return await DI.findOne({
        externalDiId: externalId
    })
};

const getAllDi = async () => {
    return await DI.find();
};

module.exports = {
    createDI,
    getAllDi,
    getDiByExternalId,
};
