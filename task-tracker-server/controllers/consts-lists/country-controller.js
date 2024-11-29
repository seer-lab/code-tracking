// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const ERRORS = require('../../consts/errors').ERRORS;
const LOGGER_NAME = require('../../consts/consts').LOGGER_NAME;
const countryService = require('../../services/consts-lists/country-service');

const logger = intelLogger.getLogger(LOGGER_NAME);

const getCountryByKey = async (key) => {
    const country = await countryService.getCountryByKey(key);

    if (!country) {
        logger.error(`${new Date()}: Country ${key} is not exists`, new Error(`Country ${key} is not exists`));
        return {
            error: ERRORS.VALIDATION.COUNTRY.NOT_EXISTS
        }
    }

    logger.info(`${new Date()}: Country ${key} was received successfully`);
    return country;
};

const createCountry = async (key, descriptions) => {
    const country = await countryService.getCountryByKey(key);

    if (country) {
        logger.error(`${new Date()}: Country ${key} was not created`, new Error(`Country ${key} is already taken`));
        return {
            error: ERRORS.VALIDATION.COUNTRY.ALREADY_TAKEN
        }
    }

    return await countryService.createCountry(key, descriptions);
};

const deleteCountryByKey = async (key) => {
    const country = await countryService.getCountryByKey(key);

    if (!country) {
        logger.error(`${new Date()}: Country ${key} is not exists`, new Error(`Country ${key} is not exists`));
        return {
            error: ERRORS.VALIDATION.COUNTRY.NOT_EXISTS
        }
    }

    logger.info(`${new Date()}: Country ${key} was deleted successfully`);
    return await countryService.deleteCountry(country);
};

const getAllCountries = async () => {
    const countries = await countryService.getAllCountries();
    logger.info(`${new Date()}: ${countries.length} countries were received successfully`);
    return countries;
};

module.exports = {
    createCountry,
    getAllCountries,
    getCountryByKey,
    deleteCountryByKey,
};

