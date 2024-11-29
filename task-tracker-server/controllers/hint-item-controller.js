// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const ERRORS = require('../consts/errors').ERRORS;
const hintItemService = require('../services/hint-item-service');
const LOGGER_NAME = require('../consts/consts').LOGGER_NAME;

const logger = intelLogger.getLogger(LOGGER_NAME);

const createHintItem = async (codePath) => {
    try {
        const hintItem = await hintItemService.createHintItem(codePath);
        logger.info(`${new Date()}: Hint item was created successfully`);
        return hintItem;
    } catch (e) {
        logger.error(`${new Date()}: Hint item was not created`, e);
        return {
            error: ERRORS.INTERNAL_SERVER
        };
    }
};

const getHintItemByExternalId = async (externalId) => {
    const hintItem = await hintItemService.getHintItemByExternalId(externalId);
    if (!hintItem) {
        const message = `Hint item with id ${externalId} is not exists`;
        logger.error(`${new Date()}: ${message}`, new Error(message));
        return {
            error: ERRORS.VALIDATION.HINT_ITEM.NOT_EXISTS
        }
    }
    logger.info(`${new Date()}: Hint item with id ${externalId} was received successfully`);
    return hintItem;
};

const getAllHintItems = async () => {
    const hintItems = await hintItemService.getAllHintItems();
    logger.info(`${new Date()}: ${hintItems.length} hint items were received successfully`);
    return hintItems;
};

module.exports = {
    createHintItem,
    getAllHintItems,
    getHintItemByExternalId,
};
