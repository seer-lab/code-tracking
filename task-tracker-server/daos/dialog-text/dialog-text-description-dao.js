// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require("mongoose");

const DialogTextDescription = mongoose.model("DialogTextDescription");

const createDialogTextDescription = async (dialogTextDescription) => {
    const dtd = new DialogTextDescription(dialogTextDescription);
    return await dtd.save();
};

const deleteDialogTextDescription = async (dialogTextDescription) => {
    return await dialogTextDescription.remove();
};

module.exports = {
    createDialogTextDescription,
    deleteDialogTextDescription,
};
