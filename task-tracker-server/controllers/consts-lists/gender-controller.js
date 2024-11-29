// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const ERRORS = require('../../consts/errors').ERRORS;
const LOGGER_NAME = require('../../consts/consts').LOGGER_NAME;
const MAX_GENDER_COUNT = require('../../consts/consts').MAX_GENDER_COUNT;
const genderService = require('../../services/consts-lists/gender-service');

const logger = intelLogger.getLogger(LOGGER_NAME);

const getGenderByKey = async (key) => {
    const gender = await genderService.getGenderByKey(key);

    if (!gender) {
        logger.error(`${new Date()}: Gender ${key} is not exists`, new Error(`Gender ${key} is not exists`));
        return {
            error: ERRORS.VALIDATION.GENDER.NOT_EXISTS
        }
    }

    logger.info(`${new Date()}: Gender ${key} was received successfully`);
    return gender;
};

const createGender = async (key, descriptions) => {
    const gender = await genderService.getGenderByKey(key);

    if (gender) {
        logger.error(`${new Date()}: Gender ${key} was not created`, new Error(`Gender ${key} is already taken`));
        return {
            error: ERRORS.VALIDATION.GENDER.ALREADY_TAKEN
        }
    }

    const genders = await genderService.getAllGenders();
    if (genders.length === MAX_GENDER_COUNT) {
        logger.error(`${new Date()}: Gender ${key} was not created`, new Error(`Number of Genders values reached the maximum value: ${MAX_GENDER_COUNT}.`));
        return {
            error: ERRORS.VALIDATION.GENDER.MAX_LIMIT
        }
    }

    return await genderService.createGender(key, descriptions);
};

const deleteGenderByKey = async (key) => {
    const gender = await genderService.getGenderByKey(key);

    if (!gender) {
        logger.error(`${new Date()}: Gender ${key} is not exists`, new Error(`Gender ${key} is not exists`));
        return {
            error: ERRORS.VALIDATION.GENDER.NOT_EXISTS
        }
    }

    logger.info(`${new Date()}: Gender ${key} was deleted successfully`);
    return await genderService.deleteGender(gender);
};

const getAllGenders = async () => {
    const genders = await genderService.getAllGenders();
    logger.info(`${new Date()}: ${genders.length} genders were received successfully`);
    return genders;
};

module.exports = {
    createGender,
    getAllGenders,
    getGenderByKey,
    deleteGenderByKey,
};

