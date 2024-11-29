// Copyright (c) 2020 Anastasiia Birillo

const diDao = require('../daos/data-item-dao');

const createDI = async (codePath, activityTrackerKey) => {
    return await diDao.createDI( codePath, activityTrackerKey);
};

const getDiByExternalId = async (externalId) => {
    return await diDao.getDiByExternalId(externalId);
};

const getAllDi = async () => {
    return await diDao.getAllDi();
};

module.exports = {
    createDI,
    getAllDi,
    getDiByExternalId
};
