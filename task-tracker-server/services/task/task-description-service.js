// Copyright (c) 2020 Anastasiia Birillo

const LANGUAGES = require('../../consts/consts').LANGUAGES;
const taskDescriptionDao = require('../../daos/task/task-description-dao');

const createTaskDescription = async (taskDescription, language) => {
    if (LANGUAGES.indexOf(language) === -1) {
        return null;
    }
    return await taskDescriptionDao.createTaskDescription(taskDescription);
};

const deleteTaskDescription = async (taskDescription) => {
    return await taskDescriptionDao.deleteTaskDescription(taskDescription);
};

module.exports = {
    createTaskDescription,
    deleteTaskDescription,
};
