// Copyright (c) 2020 Anastasiia Birillo

const TASKS = require('../../configs/task-tracker-sources/tasks');
const GENDERS = require('../../configs/task-tracker-sources/genders');
const SETTINGS = require('../../configs/task-tracker-sources/settings');
const COUNTRIES = require('../../configs/task-tracker-sources/countries');
const DIALOG_TEXTS = require('../../configs/task-tracker-sources/dialog-texts');

const taskController = require('../task-controller');
const settingsController = require('../settings-controller');
const dialogTextController = require('../dialog-text-controller');
const genderController = require('../consts-lists/gender-controller');
const countryController = require('../consts-lists/country-controller');

const createTasks = async () => {
    for (const task of TASKS) {
        await taskController.createTask(task.key, task.descriptions, task.examples);
    }
};

const createGenders = async () => {
    for (const gender of GENDERS) {
        await genderController.createGender(gender.key, gender.descriptions);
    }
};

const createSettings = async () => {
    await settingsController.createSettings(SETTINGS.descriptions);
};

const createCountries = async () => {
    for (const country of COUNTRIES) {
        await countryController.createCountry(country.key, country.descriptions);
    }
};

const createDialogTexts = async () => {
    for (const dialogText of DIALOG_TEXTS) {
        await dialogTextController.createDialogText(dialogText.key, dialogText.descriptions);
    }
};


const generateDatabase = async () => {
    await createSettings();
    await createGenders();
    await createCountries();
    await createTasks();
    await createDialogTexts();
};

module.exports = {
    generateDatabase,
};
