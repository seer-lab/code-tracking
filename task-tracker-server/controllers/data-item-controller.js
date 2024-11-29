// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const ERRORS = require('../consts/errors').ERRORS;
const diService = require('../services/data-item-service');
const LOGGER_NAME = require('../consts/consts').LOGGER_NAME;

const logger = intelLogger.getLogger(LOGGER_NAME);

const createDI = async (codePath, activityTrackerKey) => {
    try {
        const dataItem = await diService.createDI(codePath, activityTrackerKey);
        logger.info(`${new Date()}: Data item was created successfully`);
        return dataItem;
    } catch (e) {
        logger.error(`${new Date()}: Data item was not created`, e);
        return {
            error: ERRORS.INTERNAL_SERVER
        };
    }
};

const getDiByExternalId = async (externalId) => {
    const dataItem = await diService.getDiByExternalId(externalId);
    if (!dataItem) {
        const message = `Data item with id ${externalId} is not exists`;
        logger.error(`${new Date()}: ${message}`, new Error(message));
        return {
            error: ERRORS.VALIDATION.DATA_ITEM.NOT_EXISTS
        }
    }
    logger.info(`${new Date()}: Data item with id ${externalId} was received successfully`);
    return dataItem;
};

const getAllDi = async () => {
    const dataItems = await diService.getAllDi();
    logger.info(`${new Date()}: ${dataItems.length} data items were received successfully`);
    return dataItems;
};

module.exports = {
    createDI,
    getAllDi,
    getDiByExternalId,
};
