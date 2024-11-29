// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const userDao = require('../daos/user-dao');

const ERRORS = require('../consts/errors').ERRORS;
const LOGGER_NAME = require('../consts/consts').LOGGER_NAME;
const logger = intelLogger.getLogger(LOGGER_NAME);

const createUser = async () => {
    return await userDao.createUser();
};

const getUserByExternalId = async (externalId) => {
    return await userDao.getUserByExternalId(externalId);
};

const addData = async (user, diId, atiId) => {
    const isExists = user.data.findIndex(item => (item.activityTrackerKey.toString() === atiId.toString() && item.dataItemKey.toString() === diId.toString())) !== -1;
    if (isExists) {
        const message = `User with id ${user.externalStudentId} has data pair: di = ${diId} and ati = ${atiId}`;
        logger.error(`${new Date()}: ${message}`, new Error(message));
        return {
            error: ERRORS.VALIDATION.USER.DATA.ALREADY_TAKEN
        }
    }
    return await userDao.addData(user, diId, atiId)
};

const getAllUsers = async () => {
    return await userDao.getAllUsers();
};

module.exports = {
    addData,
    createUser,
    getAllUsers,
    getUserByExternalId,
};
