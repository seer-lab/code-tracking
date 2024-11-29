// Copyright (c) 2020 Anastasiia Birillo

const BASE_URL = {
    ATI: '/api/activity-tracker-item',
    USER: '/api/user',
    DI: '/api/data-item',
    HINT_ITEM: '/api/hint-item',
    TASK: '/api/task',
    DIALOG_TEXT: '/api/dialog-text',
    SETTINGS: '/api/settings',
    GENDER: '/api/gender',
    COUNTRY: '/api/country',
    EXPERIENCE: '/api/experience',
    LANGUAGE: '/api/language',
    PROGRAMMING_LANGUAGE: '/api/programming-language',
    DATABASE_GENERATOR: {
        TASK_TRACKER: `/api/database-generator/task-tracker`
    }
    
};

// Todo: in the old version we use CODE name
const DI_UPLOADED_FILE = 'tasktracker';
const ATI_UPLOADED_FILE = 'activitytracker';
const LOGGER_NAME = 'logger';
const HINT_ITEM_UPLOADED_FILE = 'hintitem';

 const LANGUAGES = ['en'];
//const LANGUAGES = ['ru', 'en'];
// const PROGRAMMING_LANGUAGES = ['python', 'java', 'kotlin', 'c++']
const PROGRAMMING_LANGUAGES = ['python']

const MAX_GENDER_COUNT = 6;

module.exports = {
    BASE_URL,
    LANGUAGES,
    LOGGER_NAME,
    DI_UPLOADED_FILE,
    ATI_UPLOADED_FILE,
    MAX_GENDER_COUNT,
    PROGRAMMING_LANGUAGES,
    HINT_ITEM_UPLOADED_FILE
};
