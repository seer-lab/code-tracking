// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const ERRORS = require('../consts/errors').ERRORS;
const diController = require('./data-item-controller');
const userService = require('../services/user-service');
const LOGGER_NAME = require('../consts/consts').LOGGER_NAME;
const atiController = require('./activity-tracker-item-controller');

const logger = intelLogger.getLogger(LOGGER_NAME);

const createUser = async () => {
    try {
        const user = await userService.createUser();
        logger.info(`${new Date()}: User was created successfully`);
        return user;
    } catch (e) {
        logger.error(`${new Date()}: User was not created`, e);
        return {
            error: ERRORS.INTERNAL_SERVER
        };
    }
};

const getUserByExternalId = async (externalId) => {
    const user = await userService.getUserByExternalId(externalId);
    if (!user) {
        const message = `User with id ${externalId} is not exists`;
        logger.error(`${new Date()}: ${message}`, new Error(message));
        return {
            error: ERRORS.VALIDATION.USER.NOT_EXISTS
        }
    }
    logger.info(`${new Date()}: User with id ${externalId} was received successfully`);
    return user;
};

const getAllUsers = async () => {
    const users = await userService.getAllUsers();
    logger.info(`${new Date()}: ${users.length} users were received successfully`);
    return users;
};

const addData = async (userId, diId, atiId) => {
    let user = await getUserByExternalId(userId);
    if (user.error) {
        return user
    }

    const di = await diController.getDiByExternalId(diId);
    if (di.error) {
        return di
    }

    if (String(atiId) !== '-1') {
        const ati = await atiController.getAtiByExternalId(atiId);
        if (ati.error) {
            return ati
        }
    }

    user = await userService.addData(user, diId, atiId);
    logger.info(`${new Date()}: user ${userId} was updates successfully. Added data: di ${diId}, ati ${atiId}`);
    return user
};

module.exports = {
    addData,
    createUser,
    getAllUsers,
    getUserByExternalId
};
