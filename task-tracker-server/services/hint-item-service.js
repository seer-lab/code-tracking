// Copyright (c) 2020 Anastasiia Birillo

const hintItemDao = require('../daos/hint-item-dao');

const createHintItem = async (codePath) => {
    return await hintItemDao.createHintItem( codePath);
};

const getHintItemByExternalId = async (externalId) => {
    return await hintItemDao.getHintItemByExternalId(externalId);
};

const getAllHintItems = async () => {
    return await hintItemDao.getAllHintItems();
};

module.exports = {
    createHintItem,
    getAllHintItems,
    getHintItemByExternalId
};
