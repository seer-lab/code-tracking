// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require("mongoose");
const User = mongoose.model("User");

const createUser = async () => {
    const user = new User({});
    return await user.save();
};

const addData = async (userId, diId, atiId) => {
    userId.data.push({
        activityTrackerKey: atiId,
        dataItemKey: diId
    });
    return await userId.save();
};

const getUserByExternalId = async (externalId) => {
    return await User.findOne({
        externalStudentId: externalId
    })
};

const getAllUsers = async () => {
    return await User.find();
};

module.exports = {
    addData,
    createUser,
    getAllUsers,
    getUserByExternalId,
};

