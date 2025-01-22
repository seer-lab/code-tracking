// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const SettingsDescriptionSchema = new Schema({
    surveyPane: {
        pin: {type: String},
        year: {type: String},
        experience: {type: String},
        // difficulty: {type: String},
        years: {type: String},
        months: {type: String},
        startSession: {type: String},
        programmingLanguage: {type: String}
    },
    taskChoosingPane: {
        chooseTask: {type: String},
        finishSession: {type: String},
        startSolving: {type: String},
        description: {type: String},
    },
    taskSolvingPane: {
        inputData: {type: String},
        outputData: {type: String},
        submit: {type: String},
        hint: {type: String},
        // Todo: delete it
        backToTasks: {type: String},
    },
    finalPane: {
        praise: {type: String},
        backToSurvey: {type: String},
        finalMessage: {type: String},
        // Todo: delete it
        backToTasks: {type: String}
    },
    commonText: {
        backToTasks: {type: String}
    },
    successPane: {
        successMessage: {type: String},
        // Todo: delete it
        backToTasks: {type: String}
    }
});

SettingsDescriptionSchema.methods.getPublicData = function () {
    let data = {
        surveyPane: this.surveyPane,
        taskChoosingPane: this.taskChoosingPane,
        taskSolvingPane: this.taskSolvingPane,
        finalPane: this.finalPane,
        successPane: this.successPane
    };
    ['taskSolvingPane', 'finalPane', 'successPane'].map(key => data[key]['backToTasks'] = this.commonText.backToTasks);
    return data;
};

module.exports = mongoose.model('SettingsDescription', SettingsDescriptionSchema);
