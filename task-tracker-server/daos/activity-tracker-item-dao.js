// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');

const ATI = mongoose.model('ActivityTrackerItem');

const createAti = async (atiData) => {
    const ati = new ATI(atiData);
    return await ati.save();
};

const getAtiByExternalId = async (externalId) => {
    return await ATI.findOne({
        externalAtiId: externalId
    })
};

const getAllAti = async () => {
    return await ATI.find();
};

module.exports = {
    createAti,
    getAtiByExternalId,
    getAllAti,
};
