// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require("mongoose");

const TaskDescription = mongoose.model("TaskDescription");

const formatterService = require('../../services/formatter-service');

const createTaskDescription = async (taskDescription) => {
    const td = new TaskDescription({
        name: formatterService.toCapitalize(taskDescription.name),
        description: taskDescription.description,
        input: taskDescription.input,
        output: taskDescription.output
    });
    return await td.save();
};

const deleteTaskDescription = async (taskDescription) => {
    return await taskDescription.remove();
};

module.exports = {
    createTaskDescription,
    deleteTaskDescription,
};
