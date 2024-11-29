// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require("mongoose");
const HintItem = mongoose.model("HintItem");

const createHintItem = async (codePath) => {
    const hintItem = new HintItem({
        codePath: codePath
    });
    return await hintItem.save();
};

const getHintItemByExternalId = async (externalId) => {
    return await HintItem.findOne({
        externalHintItemId: externalId
    })
};

const getAllHintItems = async () => {
    return await HintItem.find();
};

module.exports = {
    createHintItem,
    getAllHintItems,
    getHintItemByExternalId,
};
