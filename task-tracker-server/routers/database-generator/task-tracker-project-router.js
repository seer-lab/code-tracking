// Copyright (c) 2020 Anastasiia Birillo

const BASE_URL = require('../../consts/consts').BASE_URL;
const taskTrackerProjectController = require('../../controllers/database-generator/task-tracker-project-controller');

module.exports = (app) => {

    app.route(`${BASE_URL.DATABASE_GENERATOR.TASK_TRACKER}`).post(async (req, res, next) => {
        await taskTrackerProjectController.generateDatabase();
        res.json('Database was generated successfully');
    });
};
